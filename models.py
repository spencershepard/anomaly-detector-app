from flask import jsonify

models = ["Widget 1", "Widget 2", "Widget 3"]

def get_model_choices():
    """Returns a list of anomaly model choices for the dropdown menu."""
    return models

def classify_frame(frame):
    # Placeholder for classification logic
    print("Classifying frame...")
    class_label = "Widget 1"
    confidence = 0.85
    return jsonify({
        "class_label": class_label,
        "confidence": confidence
    })

def validate_frame(frame, model_choice):
    # Placeholder for validation logic
    print(f"Validating frame with model: {model_choice}")
    confidence = 0.95  # Example confidence score
    heat_map = "heatmap_placeholder"
    return jsonify({
        "confidence": confidence,
        "heat_map": heat_map
    })