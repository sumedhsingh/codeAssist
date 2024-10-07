from flask import Flask, jsonify, request
import requests
import os
from groq import Groq

app = Flask(__name__)

# Initialize groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Default endpoint
@app.route('/', methods=['GET'])
def default():
    return jsonify({
        "message": "Welcome to the default endpoint of snapScribe",
        "usage": "POST to /caption with JSON body: {'image_path': 'url_to_image', 'temperature': 0.7}"
    })

# Caption endpoint
@app.route('/caption', methods=['POST'])
def caption_image():
    data = request.get_json()
    image_path = data.get("image_path")
    temperature = data.get("temperature", 0.7)  # Default temperature if not provided

    if not image_path:
        return jsonify({"error": "Image path not provided"}), 400

    # Use Groq client to get image caption
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides accurate and concise captions for images."},
                {"role": "user", "content": f"Provide a brief, descriptive caption for the image located at {image_path}"}
            ],
            model="mixtral-8x7b-32768",  # Using a more capable model
            temperature=temperature,
            max_tokens=100,  # Adjust as needed
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        caption = chat_completion.choices[0].message.content
        return jsonify({"caption": caption})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)