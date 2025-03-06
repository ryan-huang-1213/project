import os
import json
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from PIL import Image, ImageDraw

app = Flask(__name__, static_folder='.', static_url_path='')

# 設定圖片標註相關資料夾
IMAGE_DIR = './train/img'
RESULT_DIR = './train/result'
DRAW_DIR = 'draw'
OUTPUT_DIR = 'media/images'

os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/train')
def train():
    images = [img for img in os.listdir(IMAGE_DIR) if img.endswith(('png', 'jpg', 'jpeg'))]
    return render_template('train.html', images=images)

@app.route('/list-files')
def list_files():
    files = [f for f in os.listdir(DRAW_DIR) if f.endswith('.py')]
    return jsonify(files)

@app.route('/read-file')
def read_file():
    file = request.args.get('file')
    with open(os.path.join(DRAW_DIR, file), 'r') as f:
        return f.read()

@app.route('/run-file')
def run_file():
    file = request.args.get('file')
    file_name = os.path.splitext(file)[0]
    output_dir = os.path.join(OUTPUT_DIR, file_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'output.png')
    file_path = os.path.join(DRAW_DIR, file)
    
    result = subprocess.run(['manim', '-ql', file_path, '-o', 'output', '-p', output_dir], capture_output=True, text=True)
    if os.path.exists(output_path):
        return jsonify({'imagePath': f'/media/images/{file_name}/output.png'})
    else:
        return jsonify({'error': 'Rendering failed', 'details': result.stderr}), 500

@app.route('/media/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route('/annotations/<filename>')
def get_annotation(filename):
    annot_path = os.path.join(RESULT_DIR, f'{filename}.json')
    if os.path.exists(annot_path):
        with open(annot_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({'points': []})

@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    data = request.json
    filename = data['filename']
    points = data['points']
    
    with open(os.path.join(RESULT_DIR, f'{filename}.json'), 'w') as f:
        json.dump({'points': points}, f)
    
    img_path = os.path.join(IMAGE_DIR, filename)
    img = Image.open(img_path).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for point in points:
        x, y = point
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0, 255))
    
    overlay.save(os.path.join(RESULT_DIR, f'{filename}.png'))
    return jsonify({'status': 'success'})

@app.route('/result/<filename>')
def get_result_image(filename):
    return send_from_directory(RESULT_DIR, filename)

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

if __name__ == '__main__':
    app.run(debug=True)
