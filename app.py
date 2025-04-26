from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)
SOLR_URL = "http://localhost:8983/solr/mycollection/select"  # <-- Your collection name here

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "*:*")
    category = request.args.get("category", "")
    published = request.args.get("published", "")

    params = {
        "q": f"title:{query}" if query else "*:*",
        "wt": "json",
        "rows": 50
    }

    fq = []
    if category:
        fq.append(f"category:{category}")
    if published:
        fq.append(f"published:{published}")
    if fq:
        params["fq"] = fq

    response = requests.get(SOLR_URL, params=params)
    docs = response.json()["response"]["docs"]
    results = [{"title": doc.get("title", ""), "author": doc.get("author", "")} for doc in docs]
    return jsonify(results)

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])

    params = {
        "q": f"title:{query}*",
        "fl": "title",
        "wt": "json",
        "rows": 5
    }

    response = requests.get(SOLR_URL, params=params)
    docs = response.json()["response"]["docs"]
    suggestions = list({doc.get("title", "") for doc in docs if "title" in doc})
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)