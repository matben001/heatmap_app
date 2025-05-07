import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.interpolate import griddata
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server


# Load the data from CSV
data = pd.read_csv("TEMP_2024-11-06_18-43-03.csv")

# 1 module of battery has 8 cells by 16, so 128 cells per module
# 1 battery has 6 modules, so 768 cells per battery 
# We have 32 sensors per module, so 192 sensors per battery
# They are arranged with 16 on one side of a battery and 16 on the other side

# In short, 12 slices of 16 sensors with maximum 12*16 per battery
# The coordinates will be within X[0,6](step 0.5), Y[0,16], Z[0,8] for a battery

# Y,Z coordinates of sensors in a module (16 sensors)
map_module = [(18.5, 5), (16, 2), (17, 7), (13.5, 1), (15, 7), (12, 2), (10, 2), (13, 7), 
              (11, 6), (9, 2), (13.5, 7), (11.5, 3), (12.5, 1), (15, 6), (15, 2), (17, 6), 
              (2.5, 5), (0.5, 1), (5, 6), (3, 2), (7.5, 7), (5.5, 3), (6.5, 1), (8.5, 5), 
              (10, 6), (7.5, 1), (9, 7), (5.5, 1), (3.5, 1), (5.5, 5), (1.5, 1), (5, 7)]

num_sensors = len(data.columns) - 1  # -1 to exclude the "Time" column
num_timestamps = data.shape[0]

# Initialize a NumPy array to store temperatures
temperatures = np.zeros((num_timestamps, num_sensors))

# Initialize empty lists for coordinates X, Y, Z and temperature of each sensor in the order of columns in the CSV
x = []
y = []
z = []
module_numbers = []
x_convert = [1, 3, 5, 4, 2, 0]

for idx, col_name in enumerate(data.columns):
    if col_name != "Time":
        # Column name is like "Module_4_Group6_Value1", so we can extract "Module", "Group" and "Value"
        i_split = col_name.split("_")
        module = int(i_split[1])  # Extract module number
        sensor = int(i_split[2][5:])  # Extract sensor number from "Group6" -> 6
        value = i_split[3][-1]  # Extract "1" or "2" to differentiate

        # Determine X coordinate for each module
        x_coord = x_convert[module]
        if module == 0 or module == 1 or module == 2:
            if 8 >= sensor or sensor >= 25:
                x_coord = x_coord + 0.5
            y_coord, z_coord = map_module[33-sensor-1]
        else:
            if 8 < sensor and sensor < 25:
                x_coord = x_coord + 0.5
            y_coord, z_coord = map_module[sensor-1]
        
        x.append(x_coord)
        y.append(y_coord)
        z.append(z_coord)
        module_numbers.append(module)
        
        # Fill the temperature array for each timestamp
        temperatures[:, idx] = data[col_name].values  # Insert temperature values

# Function to create interpolation grid
def create_interpolation_grid(x_val, points_y, points_z, temp_values):
    y_min, y_max = min(points_y), max(points_y)
    z_min, z_max = min(points_z), max(points_z)
    
    grid_y, grid_z = np.mgrid[y_min:y_max:25j, z_min:z_max:25j]
    
    # Create points for interpolation
    points = np.column_stack((points_y, points_z))
    grid_temp = griddata(points, temp_values, (grid_y, grid_z), method='cubic')
    
    return grid_y, grid_z, grid_temp

# Define the app layout
app.layout = html.Div([
    html.H1("3D Battery Temperature Visualization", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.Label("Time:"),
            dcc.Slider(
                id='time-slider',
                min=0,
                max=num_timestamps - 1,
                value=0,
                marks={i: str(i) for i in range(0, num_timestamps, max(1, num_timestamps // 10))},
                step=1
            ),
        ], style={'width': '100%', 'padding': '10px'}),
        
        html.Div([
            html.Label("Z Max:"),
            dcc.Slider(
                id='z-slider',
                min=min(z),
                max=max(z),
                value=max(z),
                marks={i: str(i) for i in [min(z), max(z)]},
                step=0.1
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Module Range:"),
            dcc.RangeSlider(
                id='module-slider',
                min=0,
                max=max(module_numbers) + 0.5,
                value=[0, max(module_numbers) + 0.5],
                marks={i: str(i) for i in range(0, max(module_numbers) + 1)},
                step=0.5
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Surface Opacity:"),
            dcc.Slider(
                id='opacity-slider',
                min=0,
                max=1,
                value=0.3,
                marks={i/10: str(i/10) for i in range(0, 11, 2)},
                step=0.05
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),
    
    dcc.Graph(id='battery-3d-graph', style={'height': '80vh'})
])

# Define callback to update the graph
@app.callback(
    Output('battery-3d-graph', 'figure'),
    [Input('time-slider', 'value'),
     Input('z-slider', 'value'),
     Input('module-slider', 'value'),
     Input('opacity-slider', 'value')]
)
def update_graph(time_index, z_max, module_range, opacity):
    x_min, x_max = module_range
    
    # Create a new figure
    fig = make_subplots(specs=[[{'type': 'scene'}]])
    
    # Filter points within the X range
    mask_x = (np.array(x) >= x_min) & (np.array(x) <= x_max)
    
    # Get unique X coordinates in the range
    unique_x = np.unique(np.array(x)[mask_x])
    
    # For temperature colorscale
    filtered_temps = temperatures[time_index][temperatures[time_index] > 0]
    if len(filtered_temps) > 0:
        temp_min = np.min(filtered_temps)
        temp_max = np.max(filtered_temps)
    else:
        temp_min, temp_max = 0, 1
    
    # Set min/max for better visualization
    temp_min = min(temp_min, 20)
    temp_max = max(temp_max, 50)
    
    # For each unique X coordinate (module position)
    for x_pos in unique_x:
        # Create mask for this X position
        mask = mask_x & (np.array(x) == x_pos) & (np.array(z) <= z_max) & (temperatures[time_index] > 0)
        
        if np.any(mask):
            # Get points for this slice
            points_y = np.array(y)[mask]
            points_z = np.array(z)[mask]
            temps = temperatures[time_index][mask]
            
            # Create interpolation grid
            grid_y, grid_z, grid_temp = create_interpolation_grid(x_pos, points_y, points_z, temps)
            
            # Remove NaN values (outside the convex hull of the input points)
            mask_valid = ~np.isnan(grid_temp)
            
            if np.any(mask_valid):
                # Create a surface plot for this X position
                x_grid = np.full_like(grid_y, x_pos)
                
                fig.add_trace(go.Surface(
                    x=x_grid,
                    y=grid_y,
                    z=grid_z,
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
                    )
                ))
            
            # Add scatter points for actual sensor positions
            fig.add_trace(go.Scatter3d(
                x=np.array(x)[mask],
                y=np.array(y)[mask],
                z=np.array(z)[mask],
                mode='markers',
                marker=dict(
                    size=5,
                    color=temperatures[time_index][mask],
                    colorscale='Jet',
                    cmin=temp_min,
                    cmax=temp_max,
                    showscale=False
                ),
                showlegend=False
            ))
    
    # Set the layout
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.5, y=-1.5, z=1)
    )
    
    fig.update_layout(
        title=f'Battery Temperature at Time {time_index}',
        scene=dict(
            xaxis_title='X-axis (Modules)',
            yaxis_title='Y-axis',
            zaxis_title='Z-axis',
            camera=camera,
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        height=800
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=10000)
