# mcp_server.py
from flask import Flask, jsonify, request, send_file
import os
import subprocess
import json

DATA_DIRS = ['/mnt/data', './data', '.']  # will search these for files

def find_data_dir():
    for d in DATA_DIRS:
        if os.path.isdir(d) and len(os.listdir(d))>0:
            return d
    return '.'

DATA_DIR = find_data_dir()

app = Flask(__name__)

@app.route('/files', methods=['GET'])
def list_files():
    files = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if os.path.isfile(os.path.join(DATA_DIR, fname)):
            files.append(fname)
    return jsonify({'files': files, 'data_dir': DATA_DIR})

@app.route('/predict', methods=['GET'])
def predict():
    """
    Params:
      file: filename relative to DATA_DIR
      column: column name
    """
    fname = request.args.get('file')
    column = request.args.get('column')
    if not fname or not column:
        return jsonify({'error': 'please provide file and column params'}), 400
    fpath = os.path.join(DATA_DIR, fname)
    if not os.path.exists(fpath):
        return jsonify({'error': f'file not found: {fname}'}), 404
    # call predict.py
    cmd = ['python3', 'predict.py', '--input', fpath, '--column', column]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=20)
        label = out.decode('utf-8').strip()
        return jsonify({'file': fname, 'column': column, 'label': label})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'predict failed', 'output': e.output.decode('utf-8')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parse', methods=['POST'])
def parse_file():
    """
    Body JSON:
      { "file": "<filename>" , "output": "output.csv" }
    This runs parser.py on a chosen file and returns the path to output.
    """
    body = request.get_json(force=True, silent=True)
    if body is None:
        return jsonify({'error': 'invalid json body'}), 400
    fname = body.get('file')
    outname = body.get('output', 'output.csv')
    if not fname:
        return jsonify({'error': 'file is required'}), 400
    fpath = os.path.join(DATA_DIR, fname)
    if not os.path.exists(fpath):
        return jsonify({'error': 'file not found'}), 404
    cmd = ['python3', 'parser.py', '--input', fpath, '--output', outname]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=60)
        return jsonify({'status': 'ok', 'output_file': outname, 'stdout': out.decode('utf-8')})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output.decode('utf-8')}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    p = os.path.join(DATA_DIR, filename)
    if not os.path.exists(p):
        return jsonify({'error': 'file not found'}), 404
    return send_file(p, as_attachment=True)

if __name__ == '__main__':
    print("Starting MCP server. Data dir:", DATA_DIR)
    app.run(host='0.0.0.0', port=5000, debug=True)
