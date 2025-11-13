from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import os, requests, json, time, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}

# In-memory storage for demo (in real app, use database)
gallery_data = {
    'images': [],
    'comments': {},
    'likes': {}
}

def allowed_format(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_filename(filename):
    # Weak filtering - this is the vulnerability!
    dangerous_chars = ['<script', '</script', 'javascript:', 'onerror=', 'onload=']
    filename_lower = filename.lower()
    
    for char in dangerous_chars:
        if char in filename_lower:
            return False
    return True

@app.route('/')
def index():
    return render_template('gallery.html', images=gallery_data['images'])

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['file']
    title = request.form.get('title', 'Untitled')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not allowed_format(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Check filename for dangerous content (but this is bypassable!)
    if not is_safe_filename(file.filename):
        return jsonify({'error': 'Suspicious filename detected'}), 400
    
    # Save file with original filename (vulnerable!)
    file_path = os.path.normpath(os.path.join(UPLOAD_FOLDER, file.filename))
    
    if "../" in file_path or not file_path.startswith(UPLOAD_FOLDER):
        return jsonify({'error': 'Invalid path'}), 400
    
    file.save(file_path)
    
    # Add to gallery
    image_id = hashlib.md5(f"{file.filename}{time.time()}".encode()).hexdigest()[:8]
    image_data = {
        'id': image_id,
        'filename': file.filename,
        'title': title,
        'description': description,
        'url': f'/static/uploads/{file.filename}',
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'uploader': session.get('username', 'Anonymous')
    }
    
    gallery_data['images'].append(image_data)
    gallery_data['comments'][image_id] = []
    gallery_data['likes'][image_id] = 0

    return jsonify({'success': True, 'image_id': image_id, 'message': 'Image uploaded successfully!'}), 200

@app.route('/image/<image_id>')
def view_image(image_id):
    image = None
    for img in gallery_data['images']:
        if img['id'] == image_id:
            image = img
            break
    
    if not image:
        return "Image not found", 404
    
    comments = gallery_data['comments'].get(image_id, [])
    likes = gallery_data['likes'].get(image_id, 0)
    
    return render_template('image_detail.html', image=image, comments=comments, likes=likes)

@app.route('/like/<image_id>', methods=['POST'])
def like_image(image_id):
    if image_id in gallery_data['likes']:
        gallery_data['likes'][image_id] += 1
        return jsonify({'success': True, 'likes': gallery_data['likes'][image_id]})
    return jsonify({'error': 'Image not found'}), 404

@app.route('/comment/<image_id>', methods=['POST'])
def add_comment(image_id):
    comment_text = request.form.get('comment', '').strip()
    username = session.get('username', 'Anonymous')
    
    if not comment_text:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    if image_id not in gallery_data['comments']:
        return jsonify({'error': 'Image not found'}), 404
    
    # XSS vulnerability: No comment sanitization!
    comment = {
        'username': username,
        'text': comment_text,  # Stored XSS vulnerability
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    gallery_data['comments'][image_id].append(comment)
    return jsonify({'success': True, 'comment': comment})

@app.route('/admin')
def admin_panel():
    # Simple admin panel - bot will visit this
    return render_template('admin.html', 
                         images=gallery_data['images'], 
                         total_images=len(gallery_data['images']))

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        url = request.form.get('url')
        reason = request.form.get('reason', 'Inappropriate content')
        
        if not url:
            return render_template('report.html', error='URL is required')
        
        # Send to bot for review
        try:
            response = requests.post("http://bot/report", 
                                   json={'url': url, 'reason': reason}, 
                                   timeout=10)
            
            if response.status_code == 200:
                return render_template('report.html', 
                                     success='Report submitted successfully! Admin will review it.')
            else:
                return render_template('report.html', 
                                     error='Failed to submit report. Please try again.')
        except:
            return render_template('report.html', 
                                 error='Service temporarily unavailable.')
    
    return render_template('report.html')

@app.route('/api/images')
def api_images():
    return jsonify(gallery_data['images'])

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        for image in gallery_data['images']:
            if (query.lower() in image['title'].lower() or 
                query.lower() in image['description'].lower() or
                query.lower() in image['filename'].lower()):
                results.append(image)
    
    return render_template('search.html', query=query, results=results)

# Session management
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run('0.0.0.0', 80, debug=True)
