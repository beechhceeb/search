"""
Flask app entry point. Routes only; business logic is in services/search_service.py.
"""
from flask import Flask, render_template, request, jsonify
import logging
from search.services import search_service

app = Flask(__name__)
log = logging.getLogger(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Main search page and results."""
    if request.method == "POST":
        query = request.form.get("query", "")
        if not query:
            results_list = search_service.get_popular_results()
            return render_template(
                "index.html",
                error="Please enter a search query.",
                results=results_list,
                query=query,
            )
        try:
            results_list = search_service.perform_search(query)
            mpb_link = f"https://www.mpb.com/en-uk/search?q={query}" if query else ""
            return render_template(
                "results.html", query=query, results=results_list, mpb_link=mpb_link
            )
        except Exception as e:
            log.error(f"Search error: {e}")
            results_list = search_service.get_popular_results()
            return render_template(
                "index.html",
                error="An error occurred during search.",
                results=results_list,
                query=query,
            )
    results_list = search_service.get_popular_results()
    return render_template("index.html", results=results_list, query="")


@app.route("/suggest", methods=["POST"])
def suggest():
    """AJAX endpoint for search suggestions."""
    data = request.get_json()
    partial = data.get("partial", "")
    suggestions = search_service.get_suggestions(partial)
    return jsonify({"suggestions": suggestions})


@app.errorhandler(500)
def internal_error(error):
    log.error(f"Internal server error: {error}")
    return render_template(
        "index.html",
        error="Internal server error.",
        results=search_service.get_popular_results(),
        query="",
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
