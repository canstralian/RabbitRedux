import gradio as gr
import requests

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

def launch_interface():
    """Launch the Gradio interface."""
    iface = gr.Interface(
        fn=classify_with_gradio,
        inputs=gr.Chatbot(),
        outputs="text",
        title="WhiteRabbitNeo Code Classification Chatbot",
        description="Interact with the WhiteRabbitNeo model for code classification. This interface connects to a Flask API backend.",
        theme="compact"
    )
    iface.launch(server_name="0.0.0.0", server_port=7860)