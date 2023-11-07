from flask import Flask
from flask import request
import jq
import jsonlines

app = Flask(__name__)

schemas = [schema for schema in jsonlines.open("schema.jsonl")]
authors = [author for author in jsonlines.open("authors.jsonl")]
articles = [article for article in jsonlines.open("articles.jsonl")]
db = {
    "articles": articles,
    "authors": authors
}


@app.get("/healthz")
def healthz():
    return ("", 204)


@app.get("/metrics")
def metrics():
    return ("""
# HELP active_requests number of active requests
# TYPE active_requests gauge
active_requests 1
# HELP total_requests number of total requests
# TYPE total_requests counter
total_requests 48
    """, 200, {"content-type": "text/plain"})


@app.get("/capabilities")
def capabilities():
    return {
        "versions": "^0.1.0",
        "capabilities": {
            "query": {
                "relation_comparisons": {},
                "order_by_aggregate": {},
                "foreach": {}
            },
            "mutations": {
                "nested_inserts": {},
                "returning": {}
            },
            "relationships": {}
        }
    }


@app.get("/schema")
def schema():
    for schema in schemas:
        return schema


@app.post("/query")
def query():
    for filter in jq.all(r'''
{
  "collection":
    (
      .collection
    ),
  "filter":
    (
      [
        .query.fields
        |to_entries[]
        |select(.value.type=="column")
        |{"key": .key, "value": ".\(.value.column)"}
      ]
      |map("\"\(.key)\": \(.value)")
      |join(", ")
    )
}
|".\(.collection)[]|{\(.filter)}"
    ''', request.get_json()):
        return jq.all(filter, db)


@app.post("/explain")
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }
