from flask import Flask, render_template, request, jsonify
from search.bootstrap import search_engine, matcher_weights, dataset

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query", "")
        if not query:
            pop_df = dataset.df.sort_values("count_of_buy_products", ascending=False)
            results_list = pop_df.head(10).to_dict(orient="records")
            return render_template(
                "index.html",
                error="Please enter a search query.",
                results=results_list,
                query=query,
            )
        results = search_engine.search_multi(
            query, matcher_weights=matcher_weights, top_k=10
        )
        results.drop(
            columns=[
                "model_name_embedding",
                "blob_embedding",
                "blob",
                "model_id",
                "performance_group",
                "market",
                "count_of_buy_products",
            ],
            inplace=True,
            errors="ignore",
        )
        results_list = results.to_dict(orient="records")
        # Add mpb_link for the current query (not per row)
        mpb_link = f"https://www.mpb.com/en-uk/search?q={query}" if query else ""
        return render_template(
            "results.html", query=query, results=results_list, mpb_link=mpb_link
        )
    pop_df = dataset.df.sort_values("count_of_buy_products", ascending=False)
    results_list = pop_df.head(10).to_dict(orient="records")
    return render_template("index.html", results=results_list, query="")


@app.route("/suggest", methods=["POST"])
def suggest():
    data = request.get_json()
    partial = data.get("partial", "")
    suggestions = []
    try:
        if not partial:
            pop_df = dataset.df.sort_values("count_of_buy_products", ascending=False)
            suggestions = pop_df["model_name"].dropna().astype(str).head(10).tolist()
        else:
            results = search_engine.search_multi(
                partial, matcher_weights=matcher_weights, top_k=10
            )
            suggestions = results["model_name"].dropna().astype(str).tolist()
    except Exception:
        suggestions = []
    return jsonify({"suggestions": suggestions})


if __name__ == "__main__":
    app.run(debug=True)
