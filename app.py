from flask import Flask, request, send_file, render_template_string
import os
from huffman import compress, decompress  

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Huffman Compressor</title>
  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background: #ecf0f3;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }
    .container {
        background: #ffffff;
        padding: 40px 50px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1 {
        margin-bottom: 30px;
        color: #2c3e50;
    }
    input[type="file"] {
        margin-bottom: 20px;
    }
    input[type="submit"] {
        padding: 10px 20px;
        margin: 0 10px;
        font-size: 1em;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.3s ease;
    }
    input[type="submit"]:hover {
        background: #2980b9;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📁 Huffman Compressor</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file" required><br>
      <input type="submit" value="Compress" name="action">
      <input type="submit" value="Decompress" name="action">
    </form>
  </div>
</body>
</html>
'''


RESULT_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Compression Result</title>
  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background: #f0f4f8;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100vh;
        margin: 0;
    }
    .box {
        background: white;
        padding: 30px 40px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
    }
    h2 {
        color: #27ae60;
        margin-bottom: 20px;
    }
    p {
        font-size: 1.1em;
        margin: 5px 0;
    }
    a.download-btn {
        display: inline-block;
        margin-top: 20px;
        padding: 10px 20px;
        background: #3498db;
        color: white;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        transition: background 0.3s ease;
    }
    a.download-btn:hover {
        background: #2980b9;
    }
  </style>
</head>
<body>
  <div class="box">
    <h2>✅ Compression Complete!</h2>
    <p>📄 Original Size: {{ original_size }} bytes</p>
    <p>🗜️ Compressed Size: {{ compressed_size }} bytes</p>
    <p>💯 Space Saved: {{ saved_percent }}%</p>
    <a class="download-btn" href="/download/{{ file_name }}">Download Compressed File</a>
  </div>
</body>
</html>
'''


DECOMPRESS_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Decompression Result</title>
  <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background: #f0f4f8;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100vh;
        margin: 0;
    }
    .box {
        background: white;
        padding: 30px 40px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
    }
    h2 {
        color: #9b59b6;
        margin-bottom: 20px;
    }
    p {
        font-size: 1.1em;
        margin: 5px 0;
    }
    a.download-btn {
        display: inline-block;
        margin-top: 20px;
        padding: 10px 20px;
        background: #8e44ad;
        color: white;
        border-radius: 6px;
        text-decoration: none;
        font-weight: bold;
        transition: background 0.3s ease;
    }
    a.download-btn:hover {
        background: #732d91;
    }
  </style>
</head>
<body>
  <div class="box">
    <h2>📤 Decompression Complete!</h2>
    <p>File has been successfully decompressed.</p>
    <a class="download-btn" href="/download/{{ file_name }}">Download Decompressed File</a>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if not uploaded_file:
            return '❌ No file uploaded.', 400

        filename = uploaded_file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(input_path)

        if request.form['action'] == 'Compress':
            compressed_filename = filename + ".bin"
            compressed_path = os.path.join(UPLOAD_FOLDER, compressed_filename)

            compress(input_path, compressed_path)

            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(compressed_path)
            saved_percent = round((original_size - compressed_size) / original_size * 100, 2)

            return render_template_string(RESULT_TEMPLATE,
                                          original_size=original_size,
                                          compressed_size=compressed_size,
                                          saved_percent=saved_percent,
                                          file_name=compressed_filename)

        elif request.form['action'] == 'Decompress':
            decompressed_filename = "decompressed_" + filename.replace(".bin", "")
            decompressed_path = os.path.join(UPLOAD_FOLDER, decompressed_filename)
            try:
                decompress(input_path, decompressed_path)
                return render_template_string(DECOMPRESS_TEMPLATE, file_name=decompressed_filename)
            except Exception as e:
                return f"❌ Error during decompression: {str(e)}", 500

    return render_template_string(HTML)

@app.route('/download/<file_name>')
def download(file_name):
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "❌ File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
