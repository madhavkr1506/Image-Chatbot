import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from io import BytesIO
import PIL.Image

app = Flask(__name__)

# Configure the Google AI API
api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyCN1tipRwzeZMFEG427lwEG9hhFaGzirps')  # Use environment variable for API key
genai.configure(api_key=api_key)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[]
)

# Initialize chat history as an empty list
chat_history = [{'sender': 'assistant', 'message': 'Hello, User. How can I help you today?'}]  # Default message

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Empty response with status 204 (No Content)



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chatbot", methods=['GET', 'POST'])
def chatBot():
    global chat_history  # Use global to modify the chat history
    if request.method == 'POST':
        message = request.form.get('combined_text')  # Get user input from form
        img = request.files.get('image')  # Get the image from the form

        if img:
            if message:
                img_in_memory = PIL.Image.open(img)
                
                # Send the image to Gemini API
                response = model.generate_content([message, img_in_memory])
                response_text = response.text  # Extract response text
                
                # Append the response to chat history
                chat_history.append({'sender': 'assistant', 'message': response_text})

                # Send message to Gemini and get response
                res = model.generate_content(["get the whole summary of the image each and everything", img_in_memory])
                resp_txt = res.text
                response1 = chat_session.send_message("store this data" + resp_txt)  # Send the user's message
                response_text1 = response1.text  # Extract response text

                # Append Gemini response to chat history
                chat_history.append({'sender': 'assistant', 'message': response_text1})

                # Return the response from Gemini API
                return response_text

        elif message:
            try:
                # Append user's message to chat history
                chat_history.append({'sender': 'user', 'message': message})

                # Send message to Gemini and get response
                response = chat_session.send_message(message)  # Send the user's message
                response_text = response.text  # Extract response text

                # Append Gemini response to chat history
                chat_history.append({'sender': 'assistant', 'message': response_text})

                # Return only the response text
                return response_text

            except Exception as e:
                return jsonify({'error': str(e)}), 500

    return render_template("index.html", chat_history=chat_history)  # Pass chat history to the template

if __name__ == "__main__":
    app.run(debug=True)
