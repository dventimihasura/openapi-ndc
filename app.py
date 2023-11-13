from flask import Flask
from flask import request
import json
import os
import requests

app = Flask(__name__)


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


@app.post("/explain")
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }


@app.get("/schema")
def schema():
    return None


@app.post("/query")
def query():
    queryRequest = request.get_json()
    response = requests.request(
        method='GET',
        url=url(queryRequest),
        headers={key: value for (key, value) in request.headers
                 if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    headers = [(name, value) for (name, value) in response.headers.items()
               if name != 'Content-Length']
    return response.content, response.status_code, headers


def url(x):
    return f'{scheme(x)}://{host(x)}:{port(x)}{path(x)}{query(x)}'


def scheme(x):
    return 'http'


def host(x):
    return os.getenv("HOST")


def port(x):
    return os.getenv("PORT")


def path(x):
    return f'/{x["collection"]}'


def query(x):
    return f'{verticalFilter(x["query"])}{horizontalFilter(x["query"]["where"])}'


def verticalFilter(x):
    return "?select=" + ",".join([value["column"]
                                  for _, value in x["fields"].items()
                                  if value["type"] == "column"])


def horizontalFilter(x):
    return "&" + ("and"
                  if x["type"] == "and"
                  else "or"
                  if x["type"] == "or"
                  else binaryComparisonOperator(x))


def binaryComparisonOperator(x):
    return f'{x["column"]["name"]}={operators[x["operator"]["name"]]}.{x["value"]["value"]}'


operators = {
    "equals": "eq",
    "like": "like"
    }




