import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash import State
from dash import callback_context
import dash_bootstrap_components as dbc
def get_css():
    return """
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
                background: transparent;
                padding: 15px;
                text-align: left;
                border: none;
                box-shadow: none;
                color: black;
                font-weight: 400;
                font-size: 16px;
            }
            .feature-card:hover {
                background: transparent;
                transform: none;
                box-shadow: none;
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
"""

# Define the app layout
def get_html_layout(num_timestamps, z):
    """
    Returns the HTML layout for the Dash app.
    This includes a hero section, quick start guide, and feature highlights.
    """


    return (
    html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src="/assets/logo.svg",
                        style={
                            "height": "80px",
                            "margin": "20px auto",
                            "display": "block",
                        },
                    ),
                ]
            ),
            # Hero Section
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                [
                                    html.I(
                                        className="fas fa-battery-three-quarters",
                                        style={"marginRight": "15px"},
                                    ),
                                    "Advanced Battery Thermal Management System",
                                ],
                                style={
                                    "fontSize": "48px",
                                    "fontWeight": "700",
                                    "marginBottom": "20px",
                                    "textAlign": "center",
                                },
                            ),
                            html.P(
                                [
                                    "Real-time 3D visualization and analysis of high-voltage battery pack thermal performance. "
                                    "Monitor temperature distributions, power consumption, and thermal management efficiency "
                                    "across 768 cells arranged in 6 modules with 192 precision sensors."
                                ],
                                style={
                                    "fontSize": "20px",
                                    "fontWeight": "300",
                                    "lineHeight": "1.6",
                                    "maxWidth": "800px",
                                    "margin": "0 auto 30px",
                                    "opacity": "0.95",
                                },
                            ),
                            # Feature highlights
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-cube",
                                                style={
                                                    "fontSize": "24px",
                                                    "marginBottom": "10px",
                                                },
                                            ),
                                            html.H4(
                                                "3D Visualization",
                                                style={
                                                    "margin": "10px 0 5px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.P(
                                                "Interactive 3D thermal mapping",
                                                style={
                                                    "fontSize": "14px",
                                                    "opacity": "0.9",
                                                },
                                            ),
                                        ],
                                        className="feature-card",
                                    ),
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-chart-line",
                                                style={
                                                    "fontSize": "24px",
                                                    "marginBottom": "10px",
                                                },
                                            ),
                                            html.H4(
                                                "Real-time Analytics",
                                                style={
                                                    "margin": "10px 0 5px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.P(
                                                "Live temperature and power trends",
                                                style={
                                                    "fontSize": "14px",
                                                    "opacity": "0.9",
                                                },
                                            ),
                                        ],
                                        className="feature-card",
                                    ),
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-thermometer-half",
                                                style={
                                                    "fontSize": "24px",
                                                    "marginBottom": "10px",
                                                },
                                            ),
                                            html.H4(
                                                "Thermal Management",
                                                style={
                                                    "margin": "10px 0 5px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.P(
                                                "Automated cooling system control",
                                                style={
                                                    "fontSize": "14px",
                                                    "opacity": "0.9",
                                                },
                                            ),
                                        ],
                                        className="feature-card",
                                    ),
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-microchip",
                                                style={
                                                    "fontSize": "24px",
                                                    "marginBottom": "10px",
                                                },
                                            ),
                                            html.H4(
                                                "Multi-sensor Array",
                                                style={
                                                    "margin": "10px 0 5px",
                                                    "fontWeight": "600",
                                                },
                                            ),
                                            html.P(
                                                "192 precision temperature sensors",
                                                style={
                                                    "fontSize": "14px",
                                                    "opacity": "0.9",
                                                },
                                            ),
                                        ],
                                        className="feature-card",
                                    ),
                                ],
                                className="feature-grid",
                            ),
                        ],
                        className="hero-content",
                    )
                ],
                className="hero-section",
            ),
            html.Div(
                [
                    # Quick Start Guide
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        [
                                            html.I(
                                                className="fas fa-rocket",
                                                style={"marginRight": "10px"},
                                            ),
                                            "Quick Start Guide",
                                        ],
                                        style={
                                            "margin": "0 0 10px",
                                            "color": "white",
                                            "fontSize": "28px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.P(
                                        "Get started with the thermal management dashboard in 3 easy steps",
                                        style={
                                            "margin": "0",
                                            "opacity": "0.9",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                                className="section-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H4(
                                                        [
                                                            html.I(
                                                                className="fas fa-play-circle",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Step 1: Move through  time using the timeline",
                                                        ],
                                                        style={
                                                            "color": "#1976d2",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Use the timeline to navigate through time and see the battery temperature at different moments."
"The animation will automatically play, advancing through the timeline to show how the temperature evolves over time.",
                                                        style={"marginBottom": "10px"},
                                                    ),
                                                    html.P(
                                                        "💡 Tip: Pause at any moment to analyze specific thermal events in detail.",
                                                        className="help-text",
                                                    ),
                                                ],
                                                className="tutorial-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.H4(
                                                        [
                                                            html.I(
                                                                className="fas fa-sliders-h",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Step 2: Adjust Controls",
                                                        ],
                                                        style={
                                                            "color": "#1976d2",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Use the sliders to focus on specific areas:",
                                                        style={"marginBottom": "5px"},
                                                    ),
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                "Time Navigation: Scrub through any moment in the test"
                                                            ),
                                                            html.Li(
                                                                "Z-Axis Range: Filter by battery height to isolate layers"
                                                            ),
                                                            html.Li(
                                                                "Module Range: Focus on specific modules (0-5)"
                                                            ),
                                                            html.Li(
                                                                "Surface Opacity: Adjust transparency to see through layers"
                                                            ),
                                                        ],
                                                        style={
                                                            "marginLeft": "20px",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "💡 Tip: Lower opacity helps visualize internal temperature gradients.",
                                                        className="help-text",
                                                    ),
                                                ],
                                                className="tutorial-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.H4(
                                                        [
                                                            html.I(
                                                                className="fas fa-mouse-pointer",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Step 3: Interact with 3D View",
                                                        ],
                                                        style={
                                                            "color": "#1976d2",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Navigate the 3D visualization:",
                                                        style={"marginBottom": "5px"},
                                                    ),
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                "Click and drag to rotate the battery pack"
                                                            ),
                                                            html.Li(
                                                                "Scroll to zoom in/out"
                                                            ),
                                                            html.Li(
                                                                "Hover over sensors to see exact temperatures"
                                                            ),
                                                            html.Li(
                                                                "Right-click and drag to pan the view"
                                                            ),
                                                        ],
                                                        style={
                                                            "marginLeft": "20px",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "💡 Tip: Rotate to side view to see temperature gradients between modules.",
                                                        className="help-text",
                                                    ),
                                                ],
                                                className="tutorial-card",
                                            ),
                                        ]
                                    )
                                ],
                                className="section-content",
                            ),
                        ],
                        className="section-card",
                    ),
                    # System Overview Stats with Insights
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        [
                                            html.I(
                                                className="fas fa-tachometer-alt",
                                                style={"marginRight": "10px"},
                                            ),
                                            "System Overview",
                                        ],
                                        style={
                                            "margin": "0 0 10px",
                                            "color": "white",
                                            "fontSize": "28px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.P(
                                        "Key performance metrics and system specifications",
                                        style={
                                            "margin": "0",
                                            "opacity": "0.9",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                                className="section-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "768",
                                                        style={
                                                            "fontSize": "32px",
                                                            "fontWeight": "700",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Total Battery Cells",
                                                        style={
                                                            "margin": "5px 0 0",
                                                            "opacity": "0.9",
                                                        },
                                                    ),
                                                    html.P(
                                                        "96S8P Configuration",
                                                        style={
                                                            "fontSize": "12px",
                                                            "opacity": "0.7",
                                                        },
                                                    ),
                                                ],
                                                className="stat-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "192",
                                                        style={
                                                            "fontSize": "32px",
                                                            "fontWeight": "700",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Temperature Sensors",
                                                        style={
                                                            "margin": "5px 0 0",
                                                            "opacity": "0.9",
                                                        },
                                                    ),
                                                    html.P(
                                                        "32 per module",
                                                        style={
                                                            "fontSize": "12px",
                                                            "opacity": "0.7",
                                                        },
                                                    ),
                                                ],
                                                className="stat-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "6",
                                                        style={
                                                            "fontSize": "32px",
                                                            "fontWeight": "700",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Battery Modules",
                                                        style={
                                                            "margin": "5px 0 0",
                                                            "opacity": "0.9",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Arranged linearly",
                                                        style={
                                                            "fontSize": "12px",
                                                            "opacity": "0.7",
                                                        },
                                                    ),
                                                ],
                                                className="stat-card",
                                            ),
                                            html.Div(
                                                [
                                                    html.H3(
                                                        "35-50°C",
                                                        style={
                                                            "fontSize": "32px",
                                                            "fontWeight": "700",
                                                            "margin": "0",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Operating Range",
                                                        style={
                                                            "margin": "5px 0 0",
                                                            "opacity": "0.9",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Optimal: 35-45°C",
                                                        style={
                                                            "fontSize": "12px",
                                                            "opacity": "0.7",
                                                        },
                                                    ),
                                                ],
                                                className="stat-card",
                                            ),
                                        ],
                                        className="stats-grid",
                                    ),
                                    # Key Insights
                                    html.Div(
                                        [
                                            html.H4(
                                                [
                                                    html.I(
                                                        className="fas fa-lightbulb",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "Key Thermal Insights",
                                                ],
                                                style={
                                                    "color": "#f57c00",
                                                    "marginBottom": "15px",
                                                    "marginTop": "30px",
                                                },
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li(
                                                        "Central modules (2-3) typically run 2-3°C hotter due to reduced airflow"
                                                    ),
                                                    html.Li(
                                                        "Temperature rise lags power output by approximately 30-60 seconds"
                                                    ),
                                                    html.Li(
                                                        "Fan activation at 35°C prevents temperatures from exceeding 50°C"
                                                    ),
                                                    html.Li(
                                                        "Bottom sensors show faster cooling rates due to proximity to cooling plate"
                                                    ),
                                                ],
                                                style={"marginLeft": "20px"},
                                            ),
                                        ],
                                        className="insight-card",
                                    ),
                                ],
                                className="section-content",
                            ),
                        ],
                        className="section-card",
                    ),
                    # Control Panel with Enhanced Tooltips
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        [
                                            html.I(
                                                className="fas fa-sliders-h",
                                                style={"marginRight": "10px"},
                                            ),
                                            "Control Panel",
                                        ],
                                        style={
                                            "margin": "0 0 10px",
                                            "color": "white",
                                            "fontSize": "28px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.P(
                                        "Interactive controls for visualization parameters and time navigation",
                                        style={
                                            "margin": "0",
                                            "opacity": "0.9",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                                className="section-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-clock",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Time Navigation",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "fontSize": "16px",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Scrub through the endurance test timeline to analyze thermal events at specific moments",
                                                        className="help-text",
                                                    ),
                                                    dcc.Slider(
                                                        id="time-slider",
                                                        min=0,
                                                        max=num_timestamps - 1,
                                                        value=0,
                                                        marks={
                                                            i: f"{i}"
                                                            for i in range(
                                                                0,
                                                                num_timestamps,
                                                                max(
                                                                    1,
                                                                    num_timestamps
                                                                    // 10,
                                                                ),
                                                            )
                                                        },
                                                        step=1,
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                            "template": "Time: {value}",
                                                        },
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Button(
                                                                [
                                                                    html.I(
                                                                        className="fas fa-play",
                                                                        style={
                                                                            "marginRight": "8px"
                                                                        },
                                                                    ),
                                                                    "Play",
                                                                ],
                                                                id="play-button",
                                                                n_clicks=0,
                                                                className="play-button",
                                                                style={
                                                                    "marginTop": "15px"
                                                                },
                                                            ),
                                                            dcc.Interval(
                                                                id="interval-component",
                                                                interval=100,
                                                                n_intervals=0,
                                                                disabled=True,
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="control-item",
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-layer-group",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Z-Axis Range (Height Filter)",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "fontSize": "16px",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Filter sensors by height to focus on specific battery layers",
                                                        className="help-text",
                                                    ),
                                                    dcc.Slider(
                                                        id="z-slider",
                                                        min=min([z for z in z if z]),
                                                        max=max([z for z in z if z]),
                                                        value=max([z for z in z if z]),
                                                        marks={
                                                            i: f"{i:.1f}"
                                                            for i in [
                                                                min(
                                                                    [z for z in z if z]
                                                                ),
                                                                max(
                                                                    [z for z in z if z]
                                                                ),
                                                            ]
                                                        },
                                                        step=0.1,
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                            "template": "Max Height: {value}",
                                                        },
                                                    ),
                                                ],
                                                className="control-item",
                                            ),
                                        ],
                                        className="control-grid",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-arrows-alt-h",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Module Range (X-Axis: 0-15)",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "fontSize": "16px",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Select which modules to display (0-5 correspond to positions 0-15 on X-axis)",
                                                        className="help-text",
                                                    ),
                                                    dcc.RangeSlider(
                                                        id="module-slider",
                                                        min=0,
                                                        max=16,
                                                        value=[0, 16],
                                                        marks={
                                                            i: str(i)
                                                            for i in range(0, 17, 2)
                                                        },
                                                        step=0.5,
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                            "template": "Range: {value}",
                                                        },
                                                    ),
                                                ],
                                                className="control-item",
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-adjust",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Surface Opacity",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "fontSize": "16px",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Adjust transparency to see through thermal surfaces and view internal gradients",
                                                        className="help-text",
                                                    ),
                                                    dcc.Slider(
                                                        id="opacity-slider",
                                                        min=0,
                                                        max=1,
                                                        value=0.3,
                                                        marks={
                                                            i / 10: f"{i/10:.1f}"
                                                            for i in range(0, 11, 2)
                                                        },
                                                        step=0.05,
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                            "template": "Opacity: {value}",
                                                        },
                                                    ),
                                                ],
                                                className="control-item",
                                            ),
                                        ],
                                        className="control-grid",
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                [
                                                    html.I(
                                                        className="fas fa-cube",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "Battery Casing Visualization",
                                                ],
                                                style={
                                                    "fontWeight": "600",
                                                    "color": "#1f2c56",
                                                    "fontSize": "16px",
                                                    "marginBottom": "15px",
                                                    "display": "block",
                                                },
                                            ),
                                            html.P(
                                                "Toggle the 3D battery casing mesh to see sensor positions relative to the physical structure",
                                                className="help-text",
                                                style={"marginBottom": "10px"},
                                            ),
                                            dcc.Checklist(
                                                id="toggle-casing",
                                                options=[
                                                    {
                                                        "label": " Show 3D battery casing mesh",
                                                        "value": "show",
                                                    }
                                                ],
                                                value=["show"],
                                                inputStyle={
                                                    "marginRight": "10px",
                                                    "transform": "scale(1.2)",
                                                },
                                                labelStyle={
                                                    "display": "inline-block",
                                                    "fontSize": "14px",
                                                    "color": "#444",
                                                },
                                            ),
                                        ],
                                        className="control-item",
                                        style={"gridColumn": "span 2"},
                                    ),
                                ],
                                className="section-content",
                            ),
                        ],
                        className="section-card",
                    ),
                    # 3D Visualization with Analysis Guide
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        [
                                            html.I(
                                                className="fas fa-cube",
                                                style={"marginRight": "10px"},
                                            ),
                                            "3D Thermal Visualization",
                                        ],
                                        style={
                                            "margin": "0 0 10px",
                                            "color": "white",
                                            "fontSize": "28px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.P(
                                        "Interactive 3D representation of battery temperature distribution with interpolated thermal surfaces",
                                        style={
                                            "margin": "0",
                                            "opacity": "0.9",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                                className="section-header",
                            ),
                            html.Div(
                                [
                                    # Analysis Tips
                                    html.Div(
                                        [
                                            html.H4(
                                                [
                                                    html.I(
                                                        className="fas fa-search",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "What to Look For",
                                                ],
                                                style={
                                                    "color": "#f57c00",
                                                    "marginBottom": "15px",
                                                },
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li(
                                                        "Red zones (>45°C): Potential thermal stress areas requiring enhanced cooling"
                                                    ),
                                                    html.Li(
                                                        "Blue zones (<30°C): Well-cooled regions or low-activity cells"
                                                    ),
                                                    html.Li(
                                                        "Sharp gradients: May indicate cooling system inefficiencies or high local resistance"
                                                    ),
                                                    html.Li(
                                                        "Module boundaries: Check for thermal isolation between modules"
                                                    ),
                                                ],
                                                style={
                                                    "marginLeft": "20px",
                                                    "marginBottom": "20px",
                                                },
                                            ),
                                        ],
                                        className="insight-card",
                                    ),
                                    dcc.Graph(
                                        id="battery-3d-graph",
                                        style={
                                            "height": "70vh",
                                            "borderRadius": "12px",
                                        },
                                    ),
                                ],
                                className="section-content",
                                style={"padding": "20px"},
                            ),
                        ],
                        className="section-card",
                    ),
                    # Analytics Dashboard with Enhanced Guidance
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        [
                                            html.I(
                                                className="fas fa-chart-line",
                                                style={"marginRight": "10px"},
                                            ),
                                            "Performance Analytics",
                                        ],
                                        style={
                                            "margin": "0 0 10px",
                                            "color": "white",
                                            "fontSize": "28px",
                                            "fontWeight": "600",
                                        },
                                    ),
                                    html.P(
                                        "Comprehensive analysis of temperature trends, power consumption, and thermal management system performance",
                                        style={
                                            "margin": "0",
                                            "opacity": "0.9",
                                            "fontSize": "16px",
                                        },
                                    ),
                                ],
                                className="section-header",
                            ),
                            html.Div(
                                [
                                    # Temperature Trends Section
                                    html.Div(
                                        [
                                            html.H3(
                                                [
                                                    html.I(
                                                        className="fas fa-thermometer-half",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "Temperature Analysis",
                                                ],
                                                style={
                                                    "color": "#1f2c56",
                                                    "fontSize": "22px",
                                                    "fontWeight": "600",
                                                    "marginBottom": "15px",
                                                },
                                            ),
                                            html.P(
                                                "Monitor minimum, average, and maximum temperatures across all sensors with optional derivative analysis.",
                                                style={
                                                    "color": "#666",
                                                    "marginBottom": "20px",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                            # Analysis Guide
                                            html.Div(
                                                [
                                                    html.H5(
                                                        [
                                                            html.I(
                                                                className="fas fa-info-circle",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Analysis Guide",
                                                        ],
                                                        style={
                                                            "color": "#1976d2",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Raw mode shows absolute temperatures - look for sustained periods above 45°C",
                                                        style={
                                                            "marginBottom": "5px",
                                                            "fontSize": "13px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Derivative mode shows rate of change - positive spikes indicate rapid heating events",
                                                        style={
                                                            "marginBottom": "5px",
                                                            "fontSize": "13px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Temperature spread (max-min) indicates thermal uniformity - smaller is better",
                                                        style={"fontSize": "13px"},
                                                    ),
                                                ],
                                                className="tutorial-card",
                                                style={"marginBottom": "20px"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-eye",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "View Mode",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    dcc.RadioItems(
                                                        id="temp-view-toggle",
                                                        options=[
                                                            {
                                                                "label": " Raw Temperature Data",
                                                                "value": "raw",
                                                            },
                                                            {
                                                                "label": " Temperature Derivative (30s Smoothed)",
                                                                "value": "deriv",
                                                            },
                                                        ],
                                                        value="raw",
                                                        labelStyle={
                                                            "display": "block",
                                                            "marginBottom": "8px",
                                                            "fontSize": "14px",
                                                        },
                                                        inputStyle={
                                                            "marginRight": "8px"
                                                        },
                                                    ),
                                                ],
                                                style={"marginBottom": "20px"},
                                            ),
                                            dcc.Graph(id="temp-trends-graph"),
                                        ],
                                        style={"marginBottom": "40px"},
                                    ),
                                    # Power Analysis Section
                                    html.Div(
                                        [
                                            html.H3(
                                                [
                                                    html.I(
                                                        className="fas fa-bolt",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "Power Consumption Analysis",
                                                ],
                                                style={
                                                    "color": "#1f2c56",
                                                    "fontSize": "22px",
                                                    "fontWeight": "600",
                                                    "marginBottom": "15px",
                                                },
                                            ),
                                            html.P(
                                                "Track electrical power consumption patterns with smoothing options for trend analysis.",
                                                style={
                                                    "color": "#666",
                                                    "marginBottom": "20px",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                            # Power Insights
                                            html.Div(
                                                [
                                                    html.H5(
                                                        [
                                                            html.I(
                                                                className="fas fa-lightbulb",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Power-Temperature Correlation",
                                                        ],
                                                        style={
                                                            "color": "#f57c00",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Notice how temperature peaks follow power peaks with a 30-60 second delay. "
                                                        "This thermal lag is due to the heat capacity of the cells and cooling system response time.",
                                                        style={"fontSize": "13px"},
                                                    ),
                                                ],
                                                className="insight-card",
                                                style={"marginBottom": "20px"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        [
                                                            html.I(
                                                                className="fas fa-filter",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Processing Mode",
                                                        ],
                                                        style={
                                                            "fontWeight": "600",
                                                            "color": "#1f2c56",
                                                            "marginBottom": "10px",
                                                            "display": "block",
                                                        },
                                                    ),
                                                    dcc.RadioItems(
                                                        id="power-view-toggle",
                                                        options=[
                                                            {
                                                                "label": " Raw Power Data",
                                                                "value": "raw",
                                                            },
                                                            {
                                                                "label": " Savitzky-Golay Smoothed",
                                                                "value": "smoothed",
                                                            },
                                                        ],
                                                        value="raw",
                                                        labelStyle={
                                                            "display": "block",
                                                            "marginBottom": "8px",
                                                            "fontSize": "14px",
                                                        },
                                                        inputStyle={
                                                            "marginRight": "8px"
                                                        },
                                                    ),
                                                ],
                                                style={"marginBottom": "20px"},
                                            ),
                                            dcc.Graph(id="power-graph"),
                                        ],
                                        style={"marginBottom": "40px"},
                                    ),
                                    # Thermal Management Section
                                    html.Div(
                                        [
                                            html.H3(
                                                [
                                                    html.I(
                                                        className="fas fa-fan",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "Thermal Management System",
                                                ],
                                                style={
                                                    "color": "#1f2c56",
                                                    "fontSize": "22px",
                                                    "fontWeight": "600",
                                                    "marginBottom": "15px",
                                                },
                                            ),
                                            html.P(
                                                "Automated cooling fan speed control based on maximum battery temperature thresholds.",
                                                style={
                                                    "color": "#666",
                                                    "marginBottom": "20px",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                            # Cooling System Info
                                            html.Div(
                                                [
                                                    html.H5(
                                                        [
                                                            html.I(
                                                                className="fas fa-snowflake",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "Cooling Strategy",
                                                        ],
                                                        style={
                                                            "color": "#1976d2",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Fan remains OFF below 35°C to maximize efficiency",
                                                        style={
                                                            "marginBottom": "5px",
                                                            "fontSize": "13px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Linear ramp from 0-70 RPM between 35-50°C",
                                                        style={
                                                            "marginBottom": "5px",
                                                            "fontSize": "13px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "• Maximum cooling at 70 RPM above 50°C",
                                                        style={"fontSize": "13px"},
                                                    ),
                                                ],
                                                className="tutorial-card",
                                                style={"marginBottom": "20px"},
                                            ),
                                            dcc.Graph(id="fan-graph"),
                                        ],
                                        style={"marginBottom": "40px"},
                                    ),
                                    # State of Charge Section
                                    html.Div(
                                        [
                                            html.H3(
                                                [
                                                    html.I(
                                                        className="fas fa-battery-half",
                                                        style={"marginRight": "8px"},
                                                    ),
                                                    "State of Charge Monitoring",
                                                ],
                                                style={
                                                    "color": "#1f2c56",
                                                    "fontSize": "22px",
                                                    "fontWeight": "600",
                                                    "marginBottom": "15px",
                                                },
                                            ),
                                            html.P(
                                                "Track battery state of charge percentage over the operational timeline.",
                                                style={
                                                    "color": "#666",
                                                    "marginBottom": "20px",
                                                    "fontSize": "14px",
                                                },
                                            ),
                                            # SOC Insights
                                            html.Div(
                                                [
                                                    html.H5(
                                                        [
                                                            html.I(
                                                                className="fas fa-chart-area",
                                                                style={
                                                                    "marginRight": "8px"
                                                                },
                                                            ),
                                                            "SOC Impact on Thermals",
                                                        ],
                                                        style={
                                                            "color": "#f57c00",
                                                            "marginBottom": "10px",
                                                        },
                                                    ),
                                                    html.P(
                                                        "Lower SOC typically correlates with higher internal resistance and increased heat generation. "
                                                        "Monitor temperature rise rate at different SOC levels to optimize charging strategies.",
                                                        style={"fontSize": "13px"},
                                                    ),
                                                ],
                                                className="insight-card",
                                                style={"marginBottom": "20px"},
                                            ),
                                            dcc.Graph(id="soc-graph"),
                                        ]
                                    ),
                                ],
                                className="section-content",
                            ),
                        ],
                        className="section-card",
                    ),
                ],
                className="main-container",
            ),
        ],
        style={"fontFamily": "Inter, sans-serif", "color": "#333"},
    ),
)