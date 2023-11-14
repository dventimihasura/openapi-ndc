from flask import Flask
from flask import request
import json
import os
import requests

app = Flask(__name__)

# app.config.from_file(os.getenv("CONFIG_FILE"), load=json.load)


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
    spec = requests.request(
        method='GET',
        # url=f'http://{app.config["SERVER_HOST"]}:{app.config["SERVER_PORT"]}'
        url=f'http://{os.getenv["SERVER_HOST"]}:{os.getenv["SERVER_PORT"]}'
    ).json()
    scalar_types = {
        "integer": {
            "aggregate_functions": {},
            "comparison_operators": {}
        },
        "string": {
            "aggregate_functions": {},
            "comparison_operators": {}
            }
        }
    object_types = {
        k: {
            "fields": {
                k: {
                    "type": "named",
                    "name": v["type"]
                } for k,v in v["properties"].items()
            }
        } for k,v in spec["components"]["schemas"].items()
    }
    collections = [
        {
            "name": k,
            "type": k
        } for k, v in spec["components"]["schemas"].items()
    ]
    # scalar_types = {}
    # object_types = {}
    # collections = []
    return {
        "scalar_types": scalar_types,
        "object_types": object_types,
        "collections": collections
        }


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
    return f'{scheme(x)}://{host(x)}:{port(x)}{path(x)}{query_part(x)}'


def scheme(x):
    return 'http'


def host(x):
    return os.getenv("SERVER_HOST")


def port(x):
    return os.getenv("SERVER_PORT")


def path(x):
    return f'/{x["collection"]}'


def query_part(x):
    return f'{verticalFilter(x)}{horizontalFilter(x)}'


def verticalFilter(x):
    if "query" not in x:
        return ""
    if "fields" not in x["query"]:
        return ""
    return "?select=" + ",".join([value["column"]
                                  for _, value in x["query"]["fields"].items()
                                  if value["type"] == "column"])


def horizontalFilter(x):
    if "query" not in x:
        return ""
    if "where" not in x["query"]:
        return ""
    return "&" + ("and"
                  if x["query"]["where"]["type"] == "and"
                  else "or"
                  if x["query"]["where"]["type"] == "or"
                  else binaryComparisonOperator(x))


def binaryComparisonOperator(x):
    if "query" not in x:
        return ""
    if "where" not in x["query"]:
        return ""
    return f'{x["query"]["where"]["column"]["name"]}={operators[x["query"]["where"]["operator"]["type"]]}.{x["query"]["where"]["value"]["value"]}'


operators = {
    "equals": "eq",
    "equal": "eq",
    "like": "like"
    }
