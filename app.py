from flask import Flask, request # Flask apps need the Flask libraries
import os                       # Flask apps can be configured in a
                                # variety of ways: config.py,
                                # config.json, environment variables,
                                # etc.  Here, we choose to configure
                                # with environment variables, so we
                                # need the os package.
import requests                 # Upstream requests to an HTTP
                                # micro-service need something like
                                # the request library

app = Flask(__name__)           # Entry-point to all Flask apps

# Public API functions

@app.get("/healthz")            # Hasura NDC spec path:  healthz
def healthz():
    return ("", 204)


@app.get("/metrics")            # Hasura NDC spec path:  metrics
def metrics():
    return ("""
# HELP active_requests number of active requests
# TYPE active_requests gauge
active_requests 1
# HELP total_requests number of total requests
# TYPE total_requests counter
total_requests 48
    """, 200, {"content-type": "text/plain"})


@app.get("/capabilities")       # Hasura NDC spec path:  capabilities
def capabilities():
    return {
        "versions": "^0.1.0",
        "capabilities": {
            "query": {
                "relation_comparisons": {},
                "order_by_aggregate": {},
                "foreach": {}
            },
            "explain": {},
            "mutations": {
                "nested_inserts": {},
                "returning": {}
            },
            "relationships": {}
        }
    }


@app.post("/explain")           # Hasura NDC spec path:  explain
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }


@app.get("/schema")             # Hasura NDC spec path:  schema
def schema():
    spec = requests.request(
        method='GET',
        url=f'http://{os.getenv("SERVER_HOST")}:{os.getenv("SERVER_PORT")}'
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
                    "description": "",
                    "arguments": {},
                    "type": {
                        "type": "named",
                        "name": "string"
                    }
                } for k,v in v["properties"].items()
            }
        } for k,v in spec["components"]["schemas"].items()
    }
    collections = [
        {
            "name": k,
            "type": k,
            "arguments": {},
            "uniqueness_constraints": {},
            "foreign_keys": {}
        } for k, v in spec["components"]["schemas"].items()
    ]
    functions = []
    procedures = []
    return {
        "scalar_types": scalar_types,
        "object_types": object_types,
        "collections": collections,
        "functions": functions,
        "procedures": procedures
    }


@app.post("/query")             # Hasura NDC spec path:  query
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
    print(url(queryRequest))
    queryResponse = [
        {
            "rows": [
                {
                    k: {
                        "title": v
                    } for k,v in row.items()
                } for row in response.json()
            ]
        },
    ]
    if "query" in queryRequest:
        if "aggregates" in queryRequest["query"]:
            if "count" in queryRequest["query"]["aggregates"]:
                if "type" in queryRequest["query"]["aggregates"]["count"]:
                    if "star_count"==queryRequest["query"]["aggregates"]["count"]["type"]:
                        queryResponse = [
                            {
                                "aggregates": {
                                    "name": "star_count",
                                    "count": 0
                                }
                            }
                        ]
    return queryResponse, response.status_code


# Private helper functions

# The following functions roughly approximate a serializer for
# generating a textual representation of an Abstract Syntax Tree
# (https://en.wikipedia.org/wiki/Abstract_syntax_tree).  Ideally, one
# would complement this with a parser--such as a Recursive Descent
# Parser (https://en.wikipedia.org/wiki/Recursive_descent_parser)
# though though output of a parser generator would also suffice--to
# parse the input Hasura NDC QueryRequest JSON representation into its
# own AST, do a tree transformation to transform that AST into an AST
# for the target platform, and then serialize that target AST into the
# target data source language (in this case the URL syntax of the
# OAS3.0 micro-service).  In this case we take the shortcut of
# serializing the JSON representation of the QueryRequest directly
# into the target URL.

# Note that translating the input QueryRequest into the language of
# the target data source is only appropriate when the target data
# source supports similar query semantics to Hasura (i.e., attribute
# selection, filtering, limiting, joins, aggregates, etc.).  For more
# primitive target data sources without this support, a different
# style for writing an NDC is warranted, where those operations are
# simulated in-situ in the Connector code.

def url(x):
    return f'{scheme(x)}://{host(x)}:{port(x)}{path(x)}{query_part(x)}'


def scheme(x):
    return 'http'


def host(x):
    return os.getenv("SERVER_HOST")


def port(x):
    return os.getenv("SERVER_PORT")


def path(x):
    if "collection" not in x:
        return ""
    return f'/{x["collection"]}'


def query_part(x):
    parts = [verticalFilter(x), horizontalFilter(x), limit(x)]
    if not parts:
        return "?" + "&".join(parts)
    return ""


def verticalFilter(x):
    if "query" not in x:
        return ""
    if "fields" not in x["query"]:
        return ""
    return "select=" + ",".join([value["column"]
                                  for _, value in x["query"]["fields"].items()
                                  if value["type"] == "column"])


def horizontalFilter(x):
    if "query" not in x:
        return ""
    if "where" not in x["query"]:
        return ""
    return "" + ("and"
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


def limit(x):
    if "query" not in x:
        return ""
    if "limit" not in x["query"]:
        return ""
    return "" + f'limit={x["query"]["limit"]}'
    


operators = {
    "equals": "eq",
    "equal": "eq",
    "like": "like"
    }
