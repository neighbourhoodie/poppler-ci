from flask import Flask, redirect, url_for, abort, request

app = Flask(__name__)

@app.route("/")
def index():
	return """
	<h1>Poppler CI Admin</h1>
	<ul>
		<li>
			<a href="/start-ci">Start CI for a Merge Request</a>
		</li>
		<li>
			<a href="/show-results">See Result Diffs</a>
		</li>
	</ul>
	"""

@app.post("/start-ci")
def start_ci_post():
	if handle_start_ci(request):
		return redirect(url_for("start_ci_get", started="yes"))
	else:
		abort(500)

@app.get("/start-ci")
def start_ci_get():
	yes = request.args.get("started", default="no")
	if yes == "yes":
		success_message = "Build Started<br>"
	else:
		success_message = ""
	return success_message + """
		<form method="post">
			<input type="text" name="branch">
			<button type="submit">Submit</button>
		</form>
	"""

@app.get("/test")
def test_get():
	return url_for("start")

def handle_start_ci(request):
	branch = request.form["branch"]
	return start_ci_for_branch(branch)

def start_ci_for_branch(branch):
	# do the thing
	return True

@app.get("/show-results/<id>")
def show_results_get(id):
	if id:
		# load result by id from results dir and display
		return True # dummy code to make the parser happy
	else:
		# list all results:
		# - open result dir
		# - for each entry:
		#   - link entryname -> /show-results/entry-id
		return False # dumy code to make the parser happy
