import subprocess
from flask import Flask, abort, render_template, request

PREFIX = "/cmd"

app = Flask(__name__)

@app.route(PREFIX)
def index():
    return render_template("home.html")

@app.get(PREFIX + "/update-refs")
def update_refs_form():
    return render_template("update_refs_form.html")

@app.post(PREFIX + "/update-refs")
def update_refs_submit():
    build_number = request.form["build_number"]
    build_dir = f"/buildbot/outputs/poppler-builder/build-{build_number}"

    proc = subprocess.run([
        "/buildbot/refs/update",
        "--refs-path", "/buildbot/refs",
        "--poppler-path", "/tmp",
        "--from-dir", build_dir
    ], capture_output=True)

    return render_template("update_refs_result.html",
        build_dir=build_dir,
        stdout=proc.stdout.decode("utf-8"),
        stderr=proc.stderr.decode("utf-8"))
