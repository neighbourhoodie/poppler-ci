import os
import shutil
import subprocess

from flask import Flask, abort, redirect, render_template, request, url_for

PREFIX = "/cmd"

REFS_PATH = "/buildbot/refs"
OUTPUTS_PATH = "/buildbot/outputs/poppler-builder"

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
    build_dir = os.path.join(OUTPUTS_PATH, f"build-{build_number}")

    proc = subprocess.run([
        "/buildbot/refs/update",
        "--refs-path", REFS_PATH,
        "--poppler-path", "/tmp",
        "--from-dir", build_dir
    ], capture_output=True)

    return render_template("update_refs_result.html",
        build_dir=build_dir,
        stdout=proc.stdout.decode("utf-8"),
        stderr=proc.stderr.decode("utf-8"))

@app.get(PREFIX + "/cleanup")
def cleanup_builds_form():
    return render_template("cleanup_builds_form.html")

@app.post(PREFIX + "/cleanup")
def cleanup_builds_submit():
    max_builds = int(request.form["max_builds"])
    builds = os.listdir(OUTPUTS_PATH)

    def parse_dirname(dirname):
        _, num = dirname.split('-', 1)
        num = int(num)
        return (num, dirname)

    parsed = [parse_dirname(dir) for dir in builds]
    parsed.sort(reverse=True)
    to_remove = [dir for (_, dir) in parsed][max_builds:]

    for dir in to_remove:
        shutil.rmtree(os.path.join(OUTPUTS_PATH, dir))

    return redirect(url_for("index"))
