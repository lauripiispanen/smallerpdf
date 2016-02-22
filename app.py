import subprocess
import sys
import os
from flask import Flask, send_file, request, g
from tempfile import mkdtemp
from shutil import rmtree

app = Flask(__name__)

created_directories = []


def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response

@app.route("/upload", methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        dirname = mkdtemp()

        inputFile = dirname + "/in.pdf"
        outputFile = dirname + "/out.pdf"

        file.save(inputFile)

        args = [
            "gs",
            "-dNOPAUSE", "-dBATCH", "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-sOutputFile=" + outputFile,
            "-c", ".setpdfwrite",
            "-f", inputFile
        ]

        subprocess.run(args)

        @after_this_request
        def delete_temp_dir(response):
            rmtree(dirname)
            return response

        return send_file(outputFile)

    return 'no file given'


if __name__ == "__main__":
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port)
