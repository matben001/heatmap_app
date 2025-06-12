import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.interpolate import griddata
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from scipy.signal import savgol_filter

import trimesh
# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Load the data from CSV
data = pd.read_csv("data/endurance.csv")
#compute power from voltage and current colums: D4 DC Bus Current,D4 DC Bus Voltage
if 'D4 DC Bus Current' in data.columns and 'D1 DC Bus Voltage' in data.columns:
    data['POWER'] = data['D4 DC Bus Current'] * data['D1 DC Bus Voltage']

battery_mesh = trimesh.load_mesh("stl/cassing.glb")

#rotate -90 deg around z axis
battery_mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-90), [0, 0, 1]))
scale_factor = 0.032  # Adjust as needed to fit your unit scale
battery_mesh.apply_scale(scale_factor)

# Optional translation to align with your sensor grid
# E.g., shift it to center around X=3, Y=10, Z=4
translation_vector = [0, 18.5, 0]
battery_mesh.apply_translation(translation_vector)
vertices = battery_mesh.vertices
faces = battery_mesh.faces
mesh_x, mesh_y, mesh_z = vertices.T
mesh_i, mesh_j, mesh_k = faces.T


# 1 module of battery has 8 cells by 16, so 128 cells per module
# 1 battery has 6 modules, so 768 cells per battery 
# We have 32 sensors per module, so 192 sensors per battery
# They are arranged with 16 on one side of a battery and 16 on the other side

# In short, 12 slices of 16 sensors with maximum 12*16 per battery
# The coordinates will be within X[0,15], Y[0,16], Z[0,8] for a battery (updated to 0-15 range)

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
# Updated x_convert to map modules to 0-15 range with proper spacing
x_convert = [2.5, 5.0, 7.5, 10.0, 12.5, 15.0]  # 6 modules spread across 0-15 range

for idx, col_name in enumerate(temp_columns):
    # Column name is like "Module_4_Group6_Value1", so we can extract "Module", "Group" and "Value"
    i_split = col_name.split("_")
    module = int(i_split[1]) if i_split[1] != '-1' else -1  # Handle Module_-1 case
    sensor = int(i_split[2][5:])  # Extract sensor number from "Group6" -> 6
    value = i_split[3][-1]  # Extract "1" or "2" to differentiate

    # Skip Module_-1 for 3D visualization
    if module == -1:
        temperatures[:, idx] = data[col_name].values
        continue

    # Determine X coordinate for each module (now in 0-15 range)
    x_coord = x_convert[module]
    if module == 0 or module == 1 or module == 2:
        if 8 >= sensor or sensor >= 25:
            x_coord = x_coord + 0.75  # Adjusted offset for 0-15 range
        y_coord, z_coord = map_module[33-sensor-1]
    else:
        if 8 < sensor and sensor < 25:
            x_coord = x_coord + 0.75  # Adjusted offset for 0-15 range
        y_coord, z_coord = map_module[sensor-1]
    
    x.append(x_coord)
    y.append(y_coord)
    z.append(z_coord)
    module_numbers.append(module)
    
    # Fill the temperature array for each timestamp
    temperatures[:, idx] = data[col_name].values  # Insert temperature values

# Calculate temperature statistics for each timestamp
def calculate_temp_stats():
    temp_stats = []
    for i in range(num_timestamps):
        valid_temps = temperatures[i][temperatures[i] > 0]  # Filter out invalid readings
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
    
    # Create finer grid for better resolution
    grid_y, grid_z = np.mgrid[y_min:y_max:30j, z_min:z_max:30j]
    
    # Create points for interpolation
    points = np.column_stack((points_y, points_z))
    grid_temp = griddata(points, temp_values, (grid_y, grid_z), method='cubic')
    
    return grid_y, grid_z, grid_temp, width

# Define the app layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🔋 Battery Temperature Dashboard", 
                style={
                    'textAlign': 'center',
                    'color': '#1f2c56',
                    'fontSize': '42px',
                    'marginBottom': '0px',
                    'fontWeight': '700',
                }),
        html.P("Real-time thermal analysis and power trends of a high-voltage battery system.",
               style={
                   'textAlign': 'center',
                   'color': '#444',
                   'fontSize': '18px',
                   'marginTop': '5px',
                   'marginBottom': '30px',
                   'fontWeight': '300'
               })
    ], style={
        'padding': '40px 20px 20px',
        'background': 'linear-gradient(90deg, #eaf2ff 0%, #f8f9ff 100%)',
        'borderBottom': '1px solid #dfe6f3',
        'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.05)'
    }),

    # Control Panel Card
    html.Div([
        html.Div([
            html.Label("🕓 Time:", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
            dcc.Slider(
                id='time-slider',
                min=0,
                max=num_timestamps - 1,
                value=0,
                marks={i: str(i) for i in range(0, num_timestamps, max(1, num_timestamps // 10))},
                step=1
            ),
        ], style={'padding': '15px 0'}),

        html.Div([
            html.Div([
                html.Label("🧭 Z Max", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
                dcc.Slider(
                    id='z-slider',
                    min=min([z for z in z if z]),
                    max=max([z for z in z if z]),
                    value=max([z for z in z if z]),
                    marks={i: str(i) for i in [min([z for z in z if z]), max([z for z in z if z])]},
                    step=0.1
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

            html.Div([
                html.Label("📦 Module Range (X: 0-15)", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
                dcc.RangeSlider(
                    id='module-slider',
                    min=0,
                    max=16,
                    value=[0, 16],
                    marks={i: str(i) for i in range(0, 17, 2)},
                    step=0.5
                ),
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
            html.Div([
        html.Label("🧱 Show Battery Casing", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
        dcc.Checklist(
            id='toggle-casing',
            options=[{'label': 'Show casing mesh', 'value': 'show'}],
            value=['show'],
            inputStyle={'marginRight': '8px', 'marginLeft': '12px'},
            labelStyle={'display': 'inline-block', 'marginRight': '12px'}
        )
    ], style={'padding': '10px 0'}),
        html.Div([
            html.Label("🖌️ Surface Opacity", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
            dcc.Slider(
                id='opacity-slider',
                min=0,
                max=1,
                value=0.3,
                marks={i/10: str(i/10) for i in range(0, 11, 2)},
                step=0.05
            ),
        ], style={'width': '48%', 'padding': '10px'})
    ], style={
        'backgroundColor': 'white',
        'padding': '30px',
        'borderRadius': '15px',
        'margin': '20px auto',
        'maxWidth': '1100px',
        'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.06)'
    }),

    # 3D Visualization
    html.Div([
        dcc.Graph(id='battery-3d-graph', style={'height': '65vh', 'borderRadius': '12px'})
    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '15px',
        'margin': '20px auto',
        'maxWidth': '1100px',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.06)'
    }),

    # Trend Graphs
    html.Div([
        html.Div([
            html.Label("🔄 Temperature View Mode", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
            dcc.RadioItems(
                id='temp-view-toggle',
                options=[
                    {'label': 'Raw Temperature', 'value': 'raw'},
                    {'label': 'Derivative (30s Smoothed)', 'value': 'deriv'}
                ],
                value='raw',
                labelStyle={'display': 'inline-block', 'marginRight': '12px'}
            )
        ], style={'padding': '10px 0'}),
        html.Div([
            dcc.Graph(id='temp-trends-graph')
        ], style={
            'width': '100%',
            'padding': '10px',
            'display': 'inline-block',
            'verticalAlign': 'top'
        }),

        html.Div([
            dcc.Graph(id='power-graph')
        ], style={
            'width': '100%',
            'padding': '10px',
            'display': 'inline-block',
            'verticalAlign': 'top'
        }),
        #add a toggle to change to smoother power graph
        html.Div([
            html.Label("🔄 Power View Mode", style={'fontWeight': 'bold', 'color': '#1f2c56'}),
            dcc.RadioItems(
                id='power-view-toggle',
                options=[
                    {'label': 'Raw Power', 'value': 'raw'},
                    {'label': 'Smoothed Power', 'value': 'smoothed'}
                ],
                value='raw',
                labelStyle={'display': 'inline-block', 'marginRight': '12px'}
            )
        ], style={'padding': '10px 0'}),
        html.Div([
            dcc.Graph(id='fan-graph')
        ], style={
            'width': '100%',
            'padding': '10px',
            'display': 'inline-block',
            'verticalAlign': 'top'
        })
    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '15px',
        'margin': '20px auto 40px',
        'maxWidth': '1100px',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.06)'
    })

], style={
    'fontFamily': 'Segoe UI, sans-serif',
    'backgroundColor': '#f4f7fb'
})  

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
            lambda col: savgol_filter(col, window_length=5000, polyorder=2, mode='interp')
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
            window = min(501, len(y) if len(y) % 2 == 1 else len(y)-1)
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
    [Input('time-slider', 'value')]
)
def update_fan_graph(current_time):
    fig = go.Figure()
    
    # Add fan speed data if available
    if 'Fan Speed' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['fan_speed'],
            mode='lines',
            name='Fan Speed',
            line=dict(color='orange', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SOC PERCENT'],
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
        yaxis_title='Fan Speed (RPM)',
        legend=dict(x=0, y=1),
        margin=dict(l=0, r=0, b=0, t=40),
        height=400
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=False, port=10000)