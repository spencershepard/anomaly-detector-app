from flask import Flask, request, jsonify
import dash
from dash import html, dcc, callback, Input, Output
import models

server = Flask(__name__) # Consider removing if we want pure Dash
app = dash.Dash(__name__, server=server)

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
