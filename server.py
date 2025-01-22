from flask import Flask, jsonify, request, send_from_directory, send_file
import os
import subprocess

app = Flask(__name__, static_folder='.', static_url_path='')

DRAW_DIR = 'draw'
OUTPUT_DIR = 'media/images'

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/list-files')
def list_files():
    files = [f for f in os.listdir(DRAW_DIR) if f.endswith('.py')]
    return jsonify(files)

@app.route('/read-file')
def read_file():
    file = request.args.get('file')
    with open(os.path.join(DRAW_DIR, file), 'r') as f:
        code = f.read()
    return code

@app.route('/run-file')
def run_file():
    file = request.args.get('file')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'output.png')
    # 使用 Manim 渲染並生成圖片
    result = subprocess.run(['manim', '-ql', os.path.join(DRAW_DIR, file), '-o', 'output'], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    # 確保圖片文件存在
    if os.path.exists(output_path):
        return jsonify({'imagePath': f'/media/images/output.png'})
    else:
        return jsonify({'error': 'Rendering failed', 'details': result.stderr}), 500

@app.route('/media/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)