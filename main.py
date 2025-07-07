from flask import Flask, request, jsonify
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import models
import time

# loads the "darkly" template and sets it as the default
load_figure_template("darkly")

server = Flask(__name__) # Consider removing if we want pure Dash
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.DARKLY])

choices = models.get_model_choices()


app.layout = html.Div([
    html.H2("Webcam Capture with Dash"),
    dcc.Dropdown(choices, 'Widget 3', id='model-selection'),
    html.Div(id="live-feed", children=[
        html.Div(id="video-container"),
        html.Div(id="live-feed-buttons", children=[
            html.Button("Classify", id="classify-btn"),
            html.Button("Validate", id="validate-btn"),
            html.Button("Capture Frame", id="capture-btn"),
        ]),
    ]),
    html.Div(id="capture-panel", style={"display": "none"}, children=[
        html.Img(id="captured-image", src="", className="captured-frame"),
        html.Div(id="capture-buttons", children=[
            html.Button("Normal", id="normal-btn"),
            html.Button("Anomaly", id="anomaly-btn"),
            html.Button("Discard", id="discard-btn"),
        ]),
    ]),
    
    html.Script(src="/assets/webcam.js"),

])

captured_frame = None

@callback(
    [Output("capture-panel", "style"),
     Output("live-feed", "style")],
    [Input("capture-btn", "n_clicks")],
    prevent_initial_call=True
)
def update_capture_panel(n_clicks):
    time.sleep(0.01)  # Wait for javascript to process first
    global captured_frame
    if captured_frame:
        print("Captured frame exists, updating panel style")
        return [{"display": "block"}, {"display": "none"}]
    else:
        return [{"display": "none"}, {"display": "block"}]
    
@callback(
        Output("capture-panel", "style", allow_duplicate=True),
        Output("live-feed", "style" , allow_duplicate=True),
        Input("discard-btn", "n_clicks"),
        prevent_initial_call=True
)
def discard_capture(n_clicks):
    global captured_frame
    if n_clicks:
        print("Discarding capture")
        captured_frame = None
        return [{"display": "none"}, {"display": "block"}]
    return dash.no_update

# @callback(
#     Output('capture-panel', 'style'),
#     Output('live-feed', 'style'),
#     Input('validate-btn', 'n_clicks'),
#     prevent_initial_call=True
# )
# def validate_capture(n_clicks):
#     global captured_frame
#     if captured_frame:
#         print("Validating capture")
#         # Here you would typically send the captured frame to a validation endpoint
#         # For now, we just reset the captured frame
#         captured_frame = None
#         return [{"display": "none"}, {"display": "block"}]
#     return dash.no_update

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
