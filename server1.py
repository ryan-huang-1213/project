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
    file_name = os.path.splitext(file)[0]
    output_dir = os.path.join(OUTPUT_DIR, file_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'output.png')
    file_path = os.path.join(DRAW_DIR, file)
    print(f"Running file: {file_path}")
    print(f"Output path: {output_path}")
    # 使用 Manim 渲染並生成圖片
    result = subprocess.run(['manim', '-ql', file_path, '-o', 'output', '-p', output_dir], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    # 確保圖片文件存在
    if os.path.exists(output_path):
        return jsonify({'imagePath': f'/media/images/{file_name}/output.png'})
    else:
        return jsonify({'error': 'Rendering failed', 'details': result.stderr}), 500

@app.route('/media/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)