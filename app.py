import gradio as gr
import requests
from flask import Flask, request, jsonify
from transformers import pipeline
from threading import Thread

# Initialize Flask app
app = Flask(__name__)

# Load the WhiteRabbitNeo model using Hugging Face's transformers pipeline
classifier = pipeline("text-classification", model="canstralian/WhiteRabbitNeo")

@app.route('/')
def home():
    """Root endpoint displaying project information."""
    return jsonify({
        "project": "RabbitRedux - WhiteRabbitNeo Code Classification Model",
        "description": "A Transformer-based model designed for text classification of code snippets.",
        "repository": "https://github.com/canstralian/WhiteRabbitNeo",
        "author": "Stephen de Jager (canstralian)",
        "license": "Apache 2.0"
    })

@app.route('/classify', methods=['POST'])
def classify_code():
    """API endpoint to classify code snippets."""
    data = request.get_json()
    
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' field in request"}), 400

    code_snippet = data["code"]
    result = classifier(code_snippet)

    return jsonify({"code": code_snippet, "classification": result})

# Function for Gradio to call the Flask API
def classify_with_gradio(user_input):
    """Function for Gradio interface to call the Flask API for classification."""
    try:
        response = requests.post("http://127.0.0.1:5000/classify", json={"code": user_input})
        if response.status_code == 200:
            result = response.json()
            classification = result.get("classification", [{"label": "Unknown", "score": 0.0}])[0]
            return f"Prediction: {classification['label']} (Confidence: {classification['score']*100:.2f}%)"
        else:
            return "Error in classification API"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Gradio interface setup
iface = gr.Interface(
    fn=classify_with_gradio,  # Gradio calls Flask API for classification
    inputs=gr.Chatbot(),  # Chat interface for users
    outputs="text",  # Display classification result as text
    title="WhiteRabbitNeo Code Classification Chatbot",
    description="Interact with the WhiteRabbitNeo model for code classification. This interface connects to a Flask API backend.",
    theme="compact"
)

# Flask app running in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

# Launching both Flask and Gradio
if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Launch Gradio interface
    iface.launch(server_name="0.0.0.0", server_port=7860)