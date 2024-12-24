from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, session
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Preset username and password
USERNAME = 'admin'
PASSWORD = 'password'

# Folders for uploaded and edited images
UPLOAD_FOLDER = 'uploads'
EDITED_FOLDER = 'edited'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EDITED_FOLDER, exist_ok=True)

@app.route('/')
def login_page():
    """Serve the login page."""
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    username = request.form.get('username')
    password = request.form.get('password')

    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid username or password")

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))

@app.route('/editor')
def index():
    """Serve the main HTML page."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload and process the prompt."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login_page'))

    if 'image' not in request.files or 'prompt' not in request.form:
        return jsonify({'error': 'Image and prompt are required!'}), 400

    # Retrieve the uploaded image and prompt
    image = request.files['image']
    prompt = request.form['prompt']

    # Log the prompt for debugging purposes
    print(f"Received prompt: {prompt}")

    # Save the uploaded image
    filename = secure_filename(image.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)
    print(f"Image saved to: {filepath}")

    # Path for the edited image
    edited_filepath = os.path.join(EDITED_FOLDER, filename)

    # Wait for the edited image to appear in the 'edited' folder
    timeout = 300  # 5-minute timeout
    start_time = time.time()
    print("Waiting for the edited image...")
    while not os.path.exists(edited_filepath):
        time.sleep(1)
        if time.time() - start_time > timeout:
            print("Timeout: Edited image not found.")
            return jsonify({'error': 'Editing timed out. Please try again.'}), 408

    print(f"Edited image found: {edited_filepath}")
    return jsonify({'edited_image_url': f'/edited/{filename}'})

@app.route('/edited/<filename>')
def get_edited_image(filename):
    """Serve the edited image."""
    edited_filepath = os.path.join(EDITED_FOLDER, filename)
    if os.path.exists(edited_filepath):
        return send_file(edited_filepath)
    else:
        return jsonify({'error': 'Edited image not found!'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

