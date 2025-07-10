from flask import Flask, request, jsonify
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import models
import s3data
import time
import os

# loads the "darkly" template and sets it as the default
load_figure_template("darkly")

server = Flask(__name__) 
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.DARKLY])

choices = models.get_model_choices()


app.layout = html.Div([
    dbc.Container([
        html.H2("Webcam Capture with Dash", className="mb-4 text-center"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(choices, 'Widget 3', id='model-selection', className="mb-3"),
            ], width=12)
        ]),
        html.Div(id="live-feed", children=[
            html.Div(id="video-container", className="mb-3"),
            dbc.ButtonGroup([
                dbc.Button("Classify", id="classify-btn", color="primary", className="me-2"),
                dbc.Button("Validate", id="validate-btn", color="success", className="me-2"),
                dbc.Button("Capture Frame", id="capture-btn", color="warning"),
            ], className="d-flex justify-content-center mb-3"),
        ]),
        html.Div(id="capture-panel", style={"display": "none"}, children=[
            dbc.Row([
                dbc.Col([
                    html.Img(id="captured-image", src="", className="captured-frame img-fluid mb-3"),
                ], width=12, className="text-center")
            ]),
            dbc.ButtonGroup([
                dbc.Button("Normal", id="normal-data-btn", color="success", className="me-2"),
                dbc.Button("Anomaly", id="anomaly-data-btn", color="danger", className="me-2"),
                dbc.Button("Discard", id="discard-btn", color="secondary"),
            ], className="d-flex justify-content-center"),
        ]),
    ], fluid=True, className="py-4"),
    
    html.Script(src="/assets/webcam.js"),

])

captured_frame = None

def reset_to_live_feed():
    """Helper function to return to live feed view"""
    return [{"display": "none"}, {"display": "block"}]

def show_capture_panel():
    """Helper function to show capture panel"""
    return [{"display": "block"}, {"display": "none"}]

@callback(
    [Output("capture-panel", "style"),
     Output("live-feed", "style")],
    [Input("capture-btn", "n_clicks"),
     Input("discard-btn", "n_clicks"),
     Input("validate-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_panel_visibility(capture_clicks, discard_clicks, validate_clicks):
    global captured_frame
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "capture-btn":
        time.sleep(0.01)  # Wait for javascript to process first
        if captured_frame:
            print("Captured frame exists, updating panel style")
            return show_capture_panel()
        else:
            return reset_to_live_feed()
    
    elif triggered_id == "discard-btn":
        print("Discarding capture")
        captured_frame = None
        return reset_to_live_feed()
    
    elif triggered_id == "validate-btn":
        if captured_frame:
            print("Validating capture")
            # Here you would typically send the captured frame to a validation endpoint
            captured_frame = None
            return reset_to_live_feed()
    
    return dash.no_update

@callback(
    [Output("capture-panel", "style", allow_duplicate=True),
     Output("live-feed", "style", allow_duplicate=True)],
    [Input("normal-data-btn", "n_clicks"),
     Input("anomaly-data-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_data_uploads(normal_clicks, anomaly_clicks):
    global captured_frame
    
    ctx = dash.callback_context
    if not ctx.triggered or not captured_frame:
        return dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "normal-data-btn":
        category = 'good'
        prefix = 'normal'
        print("Normal data capture")
    elif triggered_id == "anomaly-data-btn":
        category = 'anomaly'
        prefix = 'anomaly'
        print("Anomaly data capture")
    else:
        return dash.no_update
    
    # Upload to S3
    image_bytes = s3data.base64_dataurl_to_bytes(captured_frame)
    success = s3data.upload_data_to_s3(
        bucket_name=os.getenv('BUCKET_NAME'),
        local_path=None,
        main_category='webcam',
        split='train',
        category=category,
        image_bytes=image_bytes,
        filename=f"{prefix}_{int(time.time())}.jpg"
    )
    
    if success:
        print(f"{prefix.capitalize()} data uploaded successfully")
    else:
        print(f"Failed to upload {prefix} data")
    
    captured_frame = None
    return reset_to_live_feed()

@server.route('/capture-frame', methods=['POST'])
def capture_frame():
    image = request.json.get('image')
    if not image:
        print ("No image data received")
        return jsonify({"error": "No image data provided"}), 400
    print("Received image data")
    global captured_frame
    captured_frame = image
    
    return jsonify({"status": "received"})

if __name__ == "__main__":
    app.run(debug=True)
