import subprocess
import sys
import os
from flask import Flask, send_file, request, Response, send_from_directory
from tempfile import mkdtemp
from shutil import rmtree
from ntpath import basename, splitext

app = Flask(__name__)

created_directories = []

def add_suffix(file):
    base, ext = splitext(basename(file))
    return base + ".compressed" + ext

@app.route("/upload", methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        dirname = mkdtemp()

        inputFile = dirname + "/in.pdf"

        file.save(inputFile)

        args = [
            "gs",
            "-dNOPAUSE", "-dBATCH", "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-sOutputFile=%stdout",
            "-c", ".setpdfwrite",
            "-f", inputFile
        ]
        proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def stream_out():
            try:
                outs, err = proc.communicate()
                yield outs
            except TimeoutExpired:
                proc.kill()
                outs, err = proc.communicate()
            finally:
                rmtree(dirname)

        resp = Response(stream_out(), mimetype='application/pdf')
        resp.headers['Content-Type'] = 'application/pdf'
        resp.headers['Content-Disposition'] = 'attachment; filename="' + add_suffix(file.filename) + '"'
        return resp

    return 'no file given'

@app.route('/')
def send_index():
    return send_from_directory('public', 'index.html')


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('public', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
