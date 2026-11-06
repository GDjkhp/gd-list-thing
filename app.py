"""Flask server for gd-list-thing.

Replaces `python -m http.server 6767`. Serves the static site (index.html,
css/, js/, data/, assets/ and the root images) from this directory, but only
those paths, so .git, app.py, README etc. are not exposed.

Run:
    python app.py                      # dev server on 0.0.0.0:6767
    gunicorn -b 0.0.0.0:6767 app:app   # production
"""
import os
import posixpath

from flask import Flask, abort, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Top-level folders that are public.
PUBLIC_DIRS = {"assets", "css", "data", "js"}
# Top-level files that are public.
PUBLIC_FILES = {"index.html", "list_icon.png", "tall_logo.png", "tall_logo_bg.png"}

app = Flask(__name__, static_folder=None)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    # Normalize first so "css/../app.py" can't hop out of a public folder.
    path = posixpath.normpath(path)
    if path.startswith(("/", "..")):
        abort(404)
    top = path.split("/", 1)[0]
    if "/" not in path:
        if path not in PUBLIC_FILES:
            abort(404)
    elif top not in PUBLIC_DIRS:
        abort(404)
    return send_from_directory(BASE_DIR, path)


@app.after_request
def no_cache(resp):
    # Match edit-and-refresh behaviour of http.server while developing,
    # so level JSON changes show up immediately.
    resp.headers["Cache-Control"] = "no-cache"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 6767)))