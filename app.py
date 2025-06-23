import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.signal import savgol_filter
from scipy.interpolate import griddata
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import State
from dash import callback_context
import dash_bootstrap_components as dbc
import trimesh
import time

# Initialize the Dash app with enhanced styling
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

server = app.server

# Load the data from CSV
data = pd.read_csv("data/endurance.csv")

# Pre - processing
if 'D4 DC Bus Current' in data.columns and 'D1 DC Bus Voltage' in data.columns:
    data['POWER'] = data['D4 DC Bus Current'] * data['D1 DC Bus Voltage']
if 'D4 DC Bus Current' in data.columns and 'D1 DC Bus Voltage' in data.columns:
    pack_internal_resistance = 0.017 / 8  # Ohms
    data['THERMAL LOSS (W)'] = (data['D4 DC Bus Current'] ** 2) * pack_internal_resistance
if 'Time' in data.columns:
    data['Time'] = pd.to_datetime(data['Time'])

data = data.iloc[::100].reset_index(drop=True)

# Load the battery casing mesh
battery_mesh = trimesh.load_mesh("stl/cassing.glb")
battery_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-90), [0, 0, 1]))
scale_factor = 0.036  # Adjust as needed to fit your unit scale
battery_mesh.apply_scale(scale_factor)
translation_vector = [0, 20.0, 0]
battery_mesh.apply_translation(translation_vector)
vertices = battery_mesh.vertices
faces = battery_mesh.faces
mesh_x, mesh_y, mesh_z = vertices.T
mesh_i, mesh_j, mesh_k = faces.T

# Y,Z coordinates of sensors in a module (16 sensors)
map_module = [(18.5, 5), (16, 2), (17, 7), (13.5, 1), (15, 7), (12, 2), (10, 2), (13, 7), 
              (11, 6), (9, 2), (13.5, 7), (11.5, 3), (12.5, 1), (15, 6), (15, 2), (17, 6), 
              (2.5, 5), (0.5, 1), (5, 6), (3, 2), (7.5, 7), (5.5, 3), (6.5, 1), (8.5, 5), 
              (10, 6), (7.5, 1), (9, 7), (5.5, 1), (3.5, 1), (5.5, 5), (1.5, 1), (5, 7)]

num_sensors = len(data.columns) - 1  # -1 to exclude the "Time" column
num_timestamps = data.shape[0]

# Get temperature columns (exclude non-temperature columns)
temp_columns = [col for col in data.columns if col.startswith('Module_') and 'Group' in col]
power_columns = [col for col in data.columns if 'POWER' in col.upper()]

# Initialize a NumPy array to store temperatures
temperatures = np.zeros((num_timestamps, len(temp_columns)))

# Initialize empty lists for coordinates X, Y, Z and temperature of each sensor in the order of columns in the CSV
x = []
y = []
z = []
module_numbers = []
x_convert = [2.5, 5.0, 7.5, 10.0, 12.5, 15.0]  # 6 modules spread across 0-15 range
#x_convert = [1,3,15,12,6,0]


for idx, col_name in enumerate(temp_columns):
    i_split = col_name.split("_")
    module = int(i_split[1]) if i_split[1] != '-1' else -1
    sensor = int(i_split[2][5:])  # Extract sensor number from "Group6" -> 6
    value = i_split[3][-1]  # Extract "1" or "2" to differentiate

    if module == -1:
        temperatures[:, idx] = data[col_name].values
        continue

    x_coord = x_convert[module]
    try:
        if module in [0, 1, 2]:
            y_coord, z_coord = map_module[sensor - 1]
        else:
            y_coord, z_coord = map_module[sensor - 1]
    except IndexError:
        print(f"[Warning] Invalid sensor index: sensor={sensor}")
        continue
    
    x.append(x_coord)
    y.append(y_coord)
    z.append(z_coord)
    module_numbers.append(module)
    
    temperatures[:, idx] = data[col_name].values

# Calculate temperature statistics for each timestamp
def calculate_temp_stats():
    temp_stats = []
    for i in range(num_timestamps):
        valid_temps = temperatures[i][temperatures[i] > 0]
        if len(valid_temps) > 0:
            temp_stats.append({
                'min_temp': np.min(valid_temps),
                'max_temp': np.max(valid_temps),
                'avg_temp': np.mean(valid_temps),
                'timestamp': i
            })
        else:
            temp_stats.append({
                'min_temp': 0,
                'max_temp': 0,
                'avg_temp': 0,
                'timestamp': i
            })
    return pd.DataFrame(temp_stats)

temp_stats_df = calculate_temp_stats()

# Calculate fan speed based on max temperature
max_temp = temp_stats_df['max_temp']
fan_speed = []
for temp in max_temp:
    if temp < 35:
        fan_speed.append(0.0)
    elif 35 <= temp < 50:
        fan_speed.append((temp - 35) / 15 * 70.0)
    else:
        fan_speed.append(70.0)
data['fan_speed'] = fan_speed

# Function to create interpolation grid with added width
def create_interpolation_grid(x_val, points_y, points_z, temp_values, width=1.5):
    y_min, y_max = min(points_y), max(points_y)
    z_min, z_max = min(points_z), max(points_z)
    
    grid_y, grid_z = np.mgrid[y_min:y_max:30j, z_min:z_max:30j]
    
    points = np.column_stack((points_y, points_z))
    grid_temp = griddata(points, temp_values, (grid_y, grid_z), method='cubic')
    
    return grid_y, grid_z, grid_temp, width

# Custom CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #9d2f48 0%, #114b99 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
            }
            .main-container {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 0;
            }
            .hero-section {
                background: linear-gradient(135deg, #9d2f48 0%, #114b99 100%);
                color: white;
                padding: 60px 20px 80px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
                opacity: 0.3;
            }
            .hero-content {
                position: relative;
                z-index: 1;
                max-width: 1200px;
                margin: 0 auto;
            }
            .section-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin: 30px auto;
                max-width: 1200px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .section-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            }
            .section-header {
                background: linear-gradient(135deg, #9d2f48 0%, #114b99 100%);
                color: white;
                padding: 25px 35px;
                margin: 0;
            }
            .section-content {
                padding: 35px;
            }
            .control-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-top: 25px;
            }
            .control-item {
                background: rgba(255, 255, 255, 0.7);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid rgba(102, 126, 234, 0.2);
                transition: all 0.3s ease;
            }
            .control-item:hover {
                background: rgba(255, 255, 255, 0.9);
                border-color: rgba(102, 126, 234, 0.4);
                transform: translateY(-2px);
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: linear-gradient(135deg, #9d2f48 0%, #114b99 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.8);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid rgba(102, 126, 234, 0.2);
                transition: all 0.3s ease;
            }
            .feature-card:hover {
                background: rgba(255, 255, 255, 0.95);
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
            }
            .play-button {
                background: linear-gradient(135deg, #9d2f48 0%, #114b99 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }
            .play-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            .tutorial-card {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border: 2px solid #1976d2;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
            }
            .insight-card {
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                border: 2px solid #f57c00;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
            }
            .help-text {
                color: #666;
                font-size: 13px;
                font-style: italic;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the app layout
app.layout = html.Div([
    
    html.Div([
        html.Img(src='/assets/logo.svg', style={
            'height': '80px',
            'margin': '20px auto',
            'display': 'block'
        }), 
    ]),
    # Hero Section
    html.Div([
        html.Div([
            html.H1([
                html.I(className="fas fa-battery-three-quarters", style={'marginRight': '15px'}),
                "Advanced Battery Thermal Management System"
            ], style={
                'fontSize': '48px',
                'fontWeight': '700',
                'marginBottom': '20px',
                'textAlign': 'center'
            }),
            html.P([
                "Real-time 3D visualization and analysis of high-voltage battery pack thermal performance. "
                "Monitor temperature distributions, power consumption, and thermal management efficiency "
                "across 768 cells arranged in 6 modules with 192 precision sensors."
            ], style={
                'fontSize': '20px',
                'fontWeight': '300',
                'lineHeight': '1.6',
                'maxWidth': '800px',
                'margin': '0 auto 30px',
                'opacity': '0.95'
            }),
            
            # Feature highlights
            html.Div([
                html.Div([
                    html.I(className="fas fa-cube", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("3D Visualization", style={'margin': '10px 0 5px', 'fontWeight': '600'}),
                    html.P("Interactive 3D thermal mapping", style={'fontSize': '14px', 'opacity': '0.9'})
                ], className="feature-card"),
                
                html.Div([
                    html.I(className="fas fa-chart-line", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Real-time Analytics", style={'margin': '10px 0 5px', 'fontWeight': '600'}),
                    html.P("Live temperature and power trends", style={'fontSize': '14px', 'opacity': '0.9'})
                ], className="feature-card"),
                
                html.Div([
                    html.I(className="fas fa-thermometer-half", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Thermal Management", style={'margin': '10px 0 5px', 'fontWeight': '600'}),
                    html.P("Automated cooling system control", style={'fontSize': '14px', 'opacity': '0.9'})
                ], className="feature-card"),
                
                html.Div([
                    html.I(className="fas fa-microchip", style={'fontSize': '24px', 'marginBottom': '10px'}),
                    html.H4("Multi-sensor Array", style={'margin': '10px 0 5px', 'fontWeight': '600'}),
                    html.P("192 precision temperature sensors", style={'fontSize': '14px', 'opacity': '0.9'})
                ], className="feature-card"),
            ], className="feature-grid")
        ], className="hero-content")
    ], className="hero-section"),

    html.Div([
        # Quick Start Guide
        html.Div([
            html.Div([
                html.H2([
                    html.I(className="fas fa-rocket", style={'marginRight': '10px'}),
                    "Quick Start Guide"
                ], style={'margin': '0 0 10px', 'color': 'white', 'fontSize': '28px', 'fontWeight': '600'}),
                html.P("Get started with the thermal management dashboard in 3 easy steps", 
                       style={'margin': '0', 'opacity': '0.9', 'fontSize': '16px'})
            ], className="section-header"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H4([html.I(className="fas fa-play-circle", style={'marginRight': '8px'}), "Step 1: Play the Animation"], 
                                style={'color': '#1976d2', 'marginBottom': '10px'}),
                        html.P("Click the Play button to watch how battery temperatures evolve over time. "
                               "The animation will automatically advance through the timeline, showing real-time thermal changes.", 
                               style={'marginBottom': '10px'}),
                        html.P("💡 Tip: Pause at any moment to analyze specific thermal events in detail.", 
                               className="help-text")
                    ], className="tutorial-card"),
                    
                    html.Div([
                        html.H4([html.I(className="fas fa-sliders-h", style={'marginRight': '8px'}), "Step 2: Adjust Controls"], 
                                style={'color': '#1976d2', 'marginBottom': '10px'}),
                        html.P("Use the sliders to focus on specific areas:", style={'marginBottom': '5px'}),
                        html.Ul([
                            html.Li("Time Navigation: Scrub through any moment in the test"),
                            html.Li("Z-Axis Range: Filter by battery height to isolate layers"),
                            html.Li("Module Range: Focus on specific modules (0-5)"),
                            html.Li("Surface Opacity: Adjust transparency to see through layers")
                        ], style={'marginLeft': '20px', 'marginBottom': '10px'}),
                        html.P("💡 Tip: Lower opacity helps visualize internal temperature gradients.", 
                               className="help-text")
                    ], className="tutorial-card"),
                    
                    html.Div([
                        html.H4([html.I(className="fas fa-mouse-pointer", style={'marginRight': '8px'}), "Step 3: Interact with 3D View"], 
                                style={'color': '#1976d2', 'marginBottom': '10px'}),
                        html.P("Navigate the 3D visualization:", style={'marginBottom': '5px'}),
                        html.Ul([
                            html.Li("Click and drag to rotate the battery pack"),
                            html.Li("Scroll to zoom in/out"),
                            html.Li("Hover over sensors to see exact temperatures"),
                            html.Li("Right-click and drag to pan the view")
                        ], style={'marginLeft': '20px', 'marginBottom': '10px'}),
                        html.P("💡 Tip: Rotate to side view to see temperature gradients between modules.", 
                               className="help-text")
                    ], className="tutorial-card"),
                ])
            ], className="section-content")
        ], className="section-card"),

        # System Overview Stats with Insights
        html.Div([
            html.Div([
                html.H2([
                    html.I(className="fas fa-tachometer-alt", style={'marginRight': '10px'}),
                    "System Overview"
                ], style={'margin': '0 0 10px', 'color': 'white', 'fontSize': '28px', 'fontWeight': '600'}),
                html.P("Key performance metrics and system specifications", 
                       style={'margin': '0', 'opacity': '0.9', 'fontSize': '16px'})
            ], className="section-header"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("768", style={'fontSize': '32px', 'fontWeight': '700', 'margin': '0'}),
                        html.P("Total Battery Cells", style={'margin': '5px 0 0', 'opacity': '0.9'}),
                        html.P("96S8P Configuration", style={'fontSize': '12px', 'opacity': '0.7'})
                    ], className="stat-card"),
                    
                    html.Div([
                        html.H3("192", style={'fontSize': '32px', 'fontWeight': '700', 'margin': '0'}),
                        html.P("Temperature Sensors", style={'margin': '5px 0 0', 'opacity': '0.9'}),
                        html.P("32 per module", style={'fontSize': '12px', 'opacity': '0.7'})
                    ], className="stat-card"),
                    
                    html.Div([
                        html.H3("6", style={'fontSize': '32px', 'fontWeight': '700', 'margin': '0'}),
                        html.P("Battery Modules", style={'margin': '5px 0 0', 'opacity': '0.9'}),
                        html.P("Arranged linearly", style={'fontSize': '12px', 'opacity': '0.7'})
                    ], className="stat-card"),
                    
                    html.Div([
                        html.H3("35-50°C", style={'fontSize': '32px', 'fontWeight': '700', 'margin': '0'}),
                        html.P("Operating Range", style={'margin': '5px 0 0', 'opacity': '0.9'}),
                        html.P("Optimal: 35-45°C", style={'fontSize': '12px', 'opacity': '0.7'})
                    ], className="stat-card"),
                ], className="stats-grid"),
                
                # Key Insights
                html.Div([
                    html.H4([html.I(className="fas fa-lightbulb", style={'marginRight': '8px'}), "Key Thermal Insights"], 
                            style={'color': '#f57c00', 'marginBottom': '15px', 'marginTop': '30px'}),
                    html.Ul([
                        html.Li("Central modules (2-3) typically run 2-3°C hotter due to reduced airflow"),
                        html.Li("Temperature rise lags power output by approximately 30-60 seconds"),
                        html.Li("Fan activation at 35°C prevents temperatures from exceeding 50°C"),
                        html.Li("Bottom sensors show faster cooling rates due to proximity to cooling plate")
                    ], style={'marginLeft': '20px'})
                ], className="insight-card"),
            ], className="section-content")
        ], className="section-card"),

        # Control Panel with Enhanced Tooltips
        html.Div([
            html.Div([
                html.H2([
                    html.I(className="fas fa-sliders-h", style={'marginRight': '10px'}),
                    "Control Panel"
                ], style={'margin': '0 0 10px', 'color': 'white', 'fontSize': '28px', 'fontWeight': '600'}),
                html.P("Interactive controls for visualization parameters and time navigation", 
                       style={'margin': '0', 'opacity': '0.9', 'fontSize': '16px'})
            ], className="section-header"),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-clock", style={'marginRight': '8px'}),
                            "Time Navigation"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'fontSize': '16px', 'marginBottom': '10px', 'display': 'block'}),
                        html.P("Scrub through the endurance test timeline to analyze thermal events at specific moments", 
                               className="help-text"),
                        dcc.Slider(
                            id='time-slider',
                            min=0,
                            max=num_timestamps - 1,
                            value=0,
                            marks={i: f'{i}' for i in range(0, num_timestamps, max(1, num_timestamps // 10))},
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": True, "template": "Time: {value}"}
                        ),
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-play", style={'marginRight': '8px'}),
                                "Play"
                            ], id='play-button', n_clicks=0, className='play-button', 
                            style={'marginTop': '15px'}),
                            dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True)
                        ])
                    ], className="control-item"),
                    
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-layer-group", style={'marginRight': '8px'}),
                            "Z-Axis Range (Height Filter)"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'fontSize': '16px', 'marginBottom': '10px', 'display': 'block'}),
                        html.P("Filter sensors by height to focus on specific battery layers", 
                               className="help-text"),
                        dcc.Slider(
                            id='z-slider',
                            min=min([z for z in z if z]),
                            max=max([z for z in z if z]),
                            value=max([z for z in z if z]),
                            marks={i: f'{i:.1f}' for i in [min([z for z in z if z]), max([z for z in z if z])]},
                            step=0.1,
                            tooltip={"placement": "bottom", "always_visible": True, "template": "Max Height: {value}"}
                        ),
                    ], className="control-item"),
                ], className="control-grid"),
                
                html.Div([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-arrows-alt-h", style={'marginRight': '8px'}),
                            "Module Range (X-Axis: 0-15)"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'fontSize': '16px', 'marginBottom': '10px', 'display': 'block'}),
                        html.P("Select which modules to display (0-5 correspond to positions 0-15 on X-axis)", 
                               className="help-text"),
                        dcc.RangeSlider(
                            id='module-slider',
                            min=0,
                            max=16,
                            value=[0, 16],
                            marks={i: str(i) for i in range(0, 17, 2)},
                            step=0.5,
                            tooltip={"placement": "bottom", "always_visible": True, "template": "Range: {value}"}
                        ),
                    ], className="control-item"),
                    
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-adjust", style={'marginRight': '8px'}),
                            "Surface Opacity"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'fontSize': '16px', 'marginBottom': '10px', 'display': 'block'}),
                        html.P("Adjust transparency to see through thermal surfaces and view internal gradients", 
                               className="help-text"),
                        dcc.Slider(
                            id='opacity-slider',
                            min=0,
                            max=1,
                            value=0.3,
                            marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)},
                            step=0.05,
                            tooltip={"placement": "bottom", "always_visible": True, "template": "Opacity: {value}"}
                        ),
                    ], className="control-item"),
                ], className="control-grid"),
                
                html.Div([
                    html.Label([
                        html.I(className="fas fa-cube", style={'marginRight': '8px'}),
                        "Battery Casing Visualization"
                    ], style={'fontWeight': '600', 'color': '#1f2c56', 'fontSize': '16px', 'marginBottom': '15px', 'display': 'block'}),
                    html.P("Toggle the 3D battery casing mesh to see sensor positions relative to the physical structure", 
                           className="help-text", style={'marginBottom': '10px'}),
                    dcc.Checklist(
                        id='toggle-casing',
                        options=[{'label': ' Show 3D battery casing mesh', 'value': 'show'}],
                        value=['show'],
                        inputStyle={'marginRight': '10px', 'transform': 'scale(1.2)'},
                        labelStyle={'display': 'inline-block', 'fontSize': '14px', 'color': '#444'}
                    )
                ], className="control-item", style={'gridColumn': 'span 2'})
            ], className="section-content")
        ], className="section-card"),

        # 3D Visualization with Analysis Guide
        html.Div([
            html.Div([
                html.H2([
                    html.I(className="fas fa-cube", style={'marginRight': '10px'}),
                    "3D Thermal Visualization"
                ], style={'margin': '0 0 10px', 'color': 'white', 'fontSize': '28px', 'fontWeight': '600'}),
                html.P("Interactive 3D representation of battery temperature distribution with interpolated thermal surfaces", 
                       style={'margin': '0', 'opacity': '0.9', 'fontSize': '16px'})
            ], className="section-header"),
            
            html.Div([
                # Analysis Tips
                html.Div([
                    html.H4([html.I(className="fas fa-search", style={'marginRight': '8px'}), "What to Look For"], 
                            style={'color': '#f57c00', 'marginBottom': '15px'}),
                    html.Ul([
                        html.Li("Red zones (>45°C): Potential thermal stress areas requiring enhanced cooling"),
                        html.Li("Blue zones (<30°C): Well-cooled regions or low-activity cells"),
                        html.Li("Sharp gradients: May indicate cooling system inefficiencies or high local resistance"),
                        html.Li("Module boundaries: Check for thermal isolation between modules")
                    ], style={'marginLeft': '20px', 'marginBottom': '20px'})
                ], className="insight-card"),
                
                dcc.Graph(id='battery-3d-graph', style={'height': '70vh', 'borderRadius': '12px'})
            ], className="section-content", style={'padding': '20px'})
        ], className="section-card"),

        # Analytics Dashboard with Enhanced Guidance
        html.Div([
            html.Div([
                html.H2([
                    html.I(className="fas fa-chart-line", style={'marginRight': '10px'}),
                    "Performance Analytics"
                ], style={'margin': '0 0 10px', 'color': 'white', 'fontSize': '28px', 'fontWeight': '600'}),
                html.P("Comprehensive analysis of temperature trends, power consumption, and thermal management system performance", 
                       style={'margin': '0', 'opacity': '0.9', 'fontSize': '16px'})
            ], className="section-header"),
            
            html.Div([
                # Temperature Trends Section
                html.Div([
                    html.H3([
                        html.I(className="fas fa-thermometer-half", style={'marginRight': '8px'}),
                        "Temperature Analysis"
                    ], style={'color': '#1f2c56', 'fontSize': '22px', 'fontWeight': '600', 'marginBottom': '15px'}),
                    html.P("Monitor minimum, average, and maximum temperatures across all sensors with optional derivative analysis.",
                           style={'color': '#666', 'marginBottom': '20px', 'fontSize': '14px'}),
                    
                    # Analysis Guide
                    html.Div([
                        html.H5([html.I(className="fas fa-info-circle", style={'marginRight': '8px'}), "Analysis Guide"], 
                                style={'color': '#1976d2', 'marginBottom': '10px'}),
                        html.P("• Raw mode shows absolute temperatures - look for sustained periods above 45°C", 
                               style={'marginBottom': '5px', 'fontSize': '13px'}),
                        html.P("• Derivative mode shows rate of change - positive spikes indicate rapid heating events", 
                               style={'marginBottom': '5px', 'fontSize': '13px'}),
                        html.P("• Temperature spread (max-min) indicates thermal uniformity - smaller is better", 
                               style={'fontSize': '13px'})
                    ], className="tutorial-card", style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-eye", style={'marginRight': '8px'}),
                            "View Mode"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.RadioItems(
                            id='temp-view-toggle',
                            options=[
                                {'label': ' Raw Temperature Data', 'value': 'raw'},
                                {'label': ' Temperature Derivative (30s Smoothed)', 'value': 'deriv'}
                            ],
                            value='raw',
                            labelStyle={'display': 'block', 'marginBottom': '8px', 'fontSize': '14px'},
                            inputStyle={'marginRight': '8px'}
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    dcc.Graph(id='temp-trends-graph')
                ], style={'marginBottom': '40px'}),

                # Power Analysis Section
                html.Div([
                    html.H3([
                        html.I(className="fas fa-bolt", style={'marginRight': '8px'}),
                        "Power Consumption Analysis"
                    ], style={'color': '#1f2c56', 'fontSize': '22px', 'fontWeight': '600', 'marginBottom': '15px'}),
                    html.P("Track electrical power consumption patterns with smoothing options for trend analysis.",
                           style={'color': '#666', 'marginBottom': '20px', 'fontSize': '14px'}),
                    
                    # Power Insights
                    html.Div([
                        html.H5([html.I(className="fas fa-lightbulb", style={'marginRight': '8px'}), "Power-Temperature Correlation"], 
                                style={'color': '#f57c00', 'marginBottom': '10px'}),
                        html.P("Notice how temperature peaks follow power peaks with a 30-60 second delay. "
                               "This thermal lag is due to the heat capacity of the cells and cooling system response time.", 
                               style={'fontSize': '13px'})
                    ], className="insight-card", style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-filter", style={'marginRight': '8px'}),
                            "Processing Mode"
                        ], style={'fontWeight': '600', 'color': '#1f2c56', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.RadioItems(
                            id='power-view-toggle',
                            options=[
                                {'label': ' Raw Power Data', 'value': 'raw'},
                                {'label': ' Savitzky-Golay Smoothed', 'value': 'smoothed'}
                            ],
                            value='raw',
                            labelStyle={'display': 'block', 'marginBottom': '8px', 'fontSize': '14px'},
                            inputStyle={'marginRight': '8px'}
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    dcc.Graph(id='power-graph')
                ], style={'marginBottom': '40px'}),

                # Thermal Management Section
                html.Div([
                    html.H3([
                        html.I(className="fas fa-fan", style={'marginRight': '8px'}),
                        "Thermal Management System"
                    ], style={'color': '#1f2c56', 'fontSize': '22px', 'fontWeight': '600', 'marginBottom': '15px'}),
                    html.P("Automated cooling fan speed control based on maximum battery temperature thresholds.",
                           style={'color': '#666', 'marginBottom': '20px', 'fontSize': '14px'}),
                    
                    # Cooling System Info
                    html.Div([
                        html.H5([html.I(className="fas fa-snowflake", style={'marginRight': '8px'}), "Cooling Strategy"], 
                                style={'color': '#1976d2', 'marginBottom': '10px'}),
                        html.P("• Fan remains OFF below 35°C to maximize efficiency", 
                               style={'marginBottom': '5px', 'fontSize': '13px'}),
                        html.P("• Linear ramp from 0-70 RPM between 35-50°C", 
                               style={'marginBottom': '5px', 'fontSize': '13px'}),
                        html.P("• Maximum cooling at 70 RPM above 50°C", 
                               style={'fontSize': '13px'})
                    ], className="tutorial-card", style={'marginBottom': '20px'}),
                    
                    dcc.Graph(id='fan-graph')
                ], style={'marginBottom': '40px'}),

                # State of Charge Section
                html.Div([
                    html.H3([
                        html.I(className="fas fa-battery-half", style={'marginRight': '8px'}),
                        "State of Charge Monitoring"
                    ], style={'color': '#1f2c56', 'fontSize': '22px', 'fontWeight': '600', 'marginBottom': '15px'}),
                    html.P("Track battery state of charge percentage over the operational timeline.",
                           style={'color': '#666', 'marginBottom': '20px', 'fontSize': '14px'}),
                    
                    # SOC Insights
                    html.Div([
                        html.H5([html.I(className="fas fa-chart-area", style={'marginRight': '8px'}), "SOC Impact on Thermals"], 
                                style={'color': '#f57c00', 'marginBottom': '10px'}),
                        html.P("Lower SOC typically correlates with higher internal resistance and increased heat generation. "
                               "Monitor temperature rise rate at different SOC levels to optimize charging strategies.", 
                               style={'fontSize': '13px'})
                    ], className="insight-card", style={'marginBottom': '20px'}),
                    
                    dcc.Graph(id='soc-graph')
                ])
            ], className="section-content")
        ], className="section-card")
    ], className="main-container")
], style={'fontFamily': 'Inter, sans-serif', 'color': '#333'}),



# Define callback to update the 3D graph
@app.callback(
    Output('battery-3d-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('z-slider', 'value'),
     Input('module-slider', 'value'),
     Input('opacity-slider', 'value'),
     Input('toggle-casing', 'value')]
)
def update_3d_graph(time_index, z_max, module_range, opacity, toggle_casing):
    x_min, x_max = module_range
    
    # Create a new figure
    fig = make_subplots(specs=[[{'type': 'scene'}]])
    
    # Filter valid coordinates (exclude Module_-1)
    valid_coords = [(i, x_val, y_val, z_val) for i, (x_val, y_val, z_val) in enumerate(zip(x, y, z)) 
                    if x_val is not None and y_val is not None and z_val is not None]
    
    if not valid_coords:
        return fig
    
    valid_indices, valid_x, valid_y, valid_z = zip(*valid_coords)
    
    # Filter points within the X range - need to account for the width offset
    # Since sensors can be offset by +/- 0.75, we need to include those in the range
    mask_x = (np.array(valid_x) >= (x_min - 1.0)) & (np.array(valid_x) <= (x_max + 1.0))
    
    # Get unique X coordinates in the range (group nearby X values)
    filtered_x = np.array(valid_x)[mask_x]
    if len(filtered_x) > 0:
        # Group X coordinates that are close together (within 1.5 units)
        unique_x = []
        sorted_x = np.sort(np.unique(filtered_x))
        for x_val in sorted_x:
            if not unique_x or abs(x_val - unique_x[-1]) > 1.5:
                unique_x.append(x_val)
        unique_x = np.array(unique_x)
    else:
        unique_x = np.array([])
    
    # For temperature colorscale
    valid_temp_indices = [valid_indices[i] for i in range(len(valid_indices)) if mask_x[i]]
    if valid_temp_indices:
        filtered_temps = temperatures[time_index][valid_temp_indices]
        filtered_temps = filtered_temps[filtered_temps > 0]
        if len(filtered_temps) > 0:
            temp_min = np.min(filtered_temps)
            temp_max = np.max(filtered_temps)
        else:
            temp_min, temp_max = 20, 50
    else:
        temp_min, temp_max = 20, 50
    
    # Set min/max for better visualization
    temp_min = min(temp_min, 20)
    temp_max = max(temp_max, 50)
    
    # For each unique X coordinate (module position)
    for x_pos in unique_x:
        # Create mask for this X position - include sensors within 1.0 unit of this position
        position_mask = (mask_x & 
                        (np.abs(np.array(valid_x) - x_pos) <= 1.0) & 
                        (np.array(valid_z) <= z_max))
        
        if np.any(position_mask):
            # Get points for this slice
            slice_indices = [valid_indices[i] for i in range(len(valid_indices)) if position_mask[i]]
            points_y = np.array(valid_y)[position_mask]
            points_z = np.array(valid_z)[position_mask]
            temps = temperatures[time_index][slice_indices]
            
            # Filter out invalid temperatures
            valid_temp_mask = temps > 0
            if np.any(valid_temp_mask):
                points_y = points_y[valid_temp_mask]
                points_z = points_z[valid_temp_mask]
                temps = temps[valid_temp_mask]
                
                # Create interpolation grid with width
                if len(points_y) > 3:  # Need at least 4 points for interpolation
                    grid_y, grid_z, grid_temp, width = create_interpolation_grid(x_pos, points_y, points_z, temps)
                    
                    # Remove NaN values (outside the convex hull of the input points)
                    mask_valid = ~np.isnan(grid_temp)
                    
                    if np.any(mask_valid):
                        # Create multiple surfaces with width (front and back faces)
                        half_width = width / 2
                        
                        # Front surface
                        x_grid_front = np.full_like(grid_y, x_pos - half_width)
                        z_grid_masked = np.where(mask_valid, grid_z, np.nan)

                        fig.add_trace(go.Surface(
                            x=x_grid_front,
                            y=grid_y,
                            z=z_grid_masked,
                            surfacecolor=grid_temp,
                            colorscale='Jet',
                            cmin=temp_min,
                            cmax=temp_max,
                            opacity=opacity,
                            showscale=True,
                            colorbar=dict(
                                title='Temperature (°C)',
                                lenmode='fraction',
                                len=0.75
                            ),
                            name=f'Module {x_pos} Front'
                        ))
                        
                        # Back surface
                        x_grid_back = np.full_like(grid_y, x_pos + half_width)
                        
                        fig.add_trace(go.Surface(
                            x=x_grid_back,
                            y=grid_y,
                            z=z_grid_masked,
                            surfacecolor=grid_temp,
                            colorscale='Jet',
                            cmin=temp_min,
                            cmax=temp_max,
                            opacity=opacity,
                            showscale=False,  # Only show colorbar once
                            name=f'Module {x_pos} Back'
                        ))
                
                # Add scatter points for actual sensor positions with larger markers
                fig.add_trace(go.Scatter3d(
                    x=[x_pos] * len(points_y),
                    y=points_y,
                    z=points_z,
                    mode='markers',
                    marker=dict(
                        size=8,  # Increased marker size
                        color=temps,
                        colorscale='Jet',
                        cmin=temp_min,
                        cmax=temp_max,
                        showscale=False,
                        line=dict(width=2, color='black')  # Add border to markers
                    ),
                     text=[f"{t:.1f} °C" for t in temps],  # Tooltip text
                    hoverinfo='text',  # Only show the temperature
                    showlegend=False,
                    name=f'Sensors {x_pos}'
                ))
    
    # Set the layout
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.5, y=-1.5, z=1)
    )
    
    # Add battery mesh
    if toggle_casing:
        fig.add_trace(go.Mesh3d(
            x=mesh_x, y=mesh_y, z=mesh_z,
            i=mesh_i, j=mesh_j, k=mesh_k,
            color='lightgray',
            opacity=0.40,
            name='Battery Case',
            showscale=False
        ))
    
    fig.update_layout(
        title=f'Battery Temperature at Time {time_index} (X-axis: 0-15 range)',
        scene=dict(
            xaxis_title='X-axis (0-15 range)',
            yaxis_title='Y-axis',
            zaxis_title='Z-axis',
            camera=camera,
            aspectmode='data',
            xaxis=dict(range=[0, 16])  # Ensure X-axis shows 0-16 range
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )
    
    return fig

# Define callback to update temperature trends
@app.callback(
    Output('temp-trends-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('temp-view-toggle', 'value')]
)
def update_temp_trends(current_time, view_mode):
    fig = go.Figure()

    if view_mode == 'raw':
        df = temp_stats_df
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['max_temp'], mode='lines', name='Max Temperature',
            line=dict(color='red', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['avg_temp'], mode='lines', name='Average Temperature',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['min_temp'], mode='lines', name='Min Temperature',
            line=dict(color='green', width=2)
        ))
        y_title = 'Temperature (°C)'
    else:
        smoothed = temp_stats_df[['min_temp', 'avg_temp', 'max_temp']].apply(
            lambda col: savgol_filter(col, window_length=50, polyorder=2, mode='interp')
        )
        deriv = smoothed.diff().fillna(0)
        deriv['timestamp'] = temp_stats_df['timestamp']

        fig.add_trace(go.Scatter(
            x=deriv['timestamp'], y=deriv['max_temp'], mode='lines', name='Max Temp Derivative',
            line=dict(color='red', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=deriv['timestamp'], y=deriv['avg_temp'], mode='lines', name='Avg Temp Derivative',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=deriv['timestamp'], y=deriv['min_temp'], mode='lines', name='Min Temp Derivative',
            line=dict(color='green', width=2)
        ))
        y_title = 'Temperature Derivative (°C/s)'

    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Current Time: {current_time}"
    )

    fig.update_layout(
        title='Temperature Trends Over Time',
        xaxis_title='Time Index',
        yaxis_title=y_title,
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40),
        height=400
    )

    return fig


# Define callback to update power graph
@app.callback(
    Output('power-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('power-view-toggle', 'value')]
)
def update_power_graph(current_time, power_view_mode):
    fig = go.Figure()
    power_col = None
    # Try to find a power column
    for col in data.columns:
        if 'POWER' in col.upper():
            power_col = col
            break
    if power_col:
        y = data[power_col]
        if power_view_mode == 'smoothed':
            # Use Savitzky-Golay filter for smoothing
            window = min(51, len(y) if len(y) % 2 == 1 else len(y)-1)
            if window < 5:
                window = 5
            if window % 2 == 0:
                window += 1
            y_smoothed = savgol_filter(y, window_length=window, polyorder=2, mode='interp')
            fig.add_trace(go.Scatter(
                x=data.index,
                y=y_smoothed,
                mode='lines',
                name='Smoothed Power',
                line=dict(color='purple', width=2, dash='dash')
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=y,
                mode='lines',
                name='Raw Power',
                line=dict(color='purple', width=2)
            ))

    # Add vertical line for current time
    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Current Time: {current_time}"
    )

    fig.update_layout(
        title='Power Over Time',
        xaxis_title='Time Index',
        yaxis_title='Power (W)',
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40),
        height=400
    )

    return fig
# Add another graph for Fan Speed
@app.callback(
    Output('fan-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('power-view-toggle', 'value')]
)
def update_fan_graph(current_time, toggle_casing):
    fig = go.Figure()
    
    # Add fan speed data if available
    if 'fan_speed' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['fan_speed'],
            mode='lines',
            name='Fan Speed',
            line=dict(color='orange', width=2)
        ))
       
    # Add vertical line for current time
    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Current Time: {current_time}"
    )
    
    fig.update_layout(
        title='Fan Speed Over Time',
        xaxis_title='Time Index',
        yaxis_title='Fan Speed (%)',
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40),
        height=400
    )
    
    return fig
#add new line graph for SOC PERCENT
@app.callback(
    Output('soc-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('power-view-toggle', 'value')]
)
def update_soc_graph(current_time, view_mode):
    fig = go.Figure()
    
    # Add SOC PERCENT data if available
    if 'SOC PERCENT' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SOC PERCENT'],
            mode='lines',
            name='SOC Percent',
            line=dict(color='green', width=2)
        ))
    
    # Add vertical line for current time
    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Current Time: {current_time}"
    )
    
    fig.update_layout(
        title='State of Charge (SOC) Over Time',
        xaxis_title='Time Index',
        yaxis_title='SOC Percent (%)',
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40),
        height=400
    )
    
    return fig

@app.callback(
    Output('time-slider', 'value'),
    Output('interval-component', 'disabled'),
    Output('play-button', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('play-button', 'n_clicks'),
    State('time-slider', 'value'),
    State('interval-component', 'disabled'),
)
def handle_play_pause_or_advance(n_intervals, n_clicks, current_value, is_disabled):
    triggered_id = callback_context.triggered_id

    if triggered_id == 'play-button':
        # Toggle play/pause
        if is_disabled:
            return current_value, False, [html.I(className="fas fa-pause", style={'marginRight': '8px'}), 'Pause']
        else:
            return current_value, True, [html.I(className="fas fa-play", style={'marginRight': '8px'}), 'Play']

    elif triggered_id == 'interval-component' and not is_disabled:
        # Wait 2 seconds before advancing
        next_value = current_value + 20
        if next_value >= num_timestamps:
            return num_timestamps - 20, True, [html.I(className="fas fa-play", style={'marginRight': '8px'}), 'Play']  # Pause at end
        return next_value, False, [html.I(className="fas fa-pause", style={'marginRight': '8px'}), 'Pause']

    raise dash.exceptions.PreventUpdate

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=10000)