import subprocess
from flask import Flask, redirect, url_for, abort, request

app = Flask(__name__)

@app.route("/cmd")
def index():
    return """
    <h1>Poppler CI Admin</h1>
    <ul>
        <li>
            <a href="/cmd/update-refs">Update refs from a build</a>
        </li>
    </ul>
    """

@app.get("/cmd/update-refs")
def update_refs_form():
    return """
    <h1>Update refs from a build</h1>

    <form method="post" action="/cmd/update-refs">
        <p><label for="build_number">Builder number</label>
            <input type="number" id="build_number" name="build_number"></p>
        <p><input type="submit" value="Go"></p>
    </form>
    """

@app.post("/cmd/update-refs")
def update_refs_submit():
    build_number = request.form["build_number"]
    build_dir = f"/buildbot/outputs/poppler-builder/build-{build_number}"
    subprocess.run([
        "/buildbot/refs/update",
        "--refs-path", "/buildbot/refs",
        "--poppler-path", "/tmp",
        "--from-dir", build_dir
    ])
    return redirect(url_for("index"))
