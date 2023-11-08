from flask import Flask
from flask import request
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


@app.get("/schema")
def schema():
    return None


@app.post("/query")
def query():
    sp = request.get_json()['collection']
    id = request.get_json()['query']['where']['value']['value']
    response = requests.request(
        method='GET',
        url=f'http://24.144.81.165:3001/{sp}?id=eq.{id}',
        headers={key: value for (key, value) in request.headers
                 if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    headers = [(name, value) for (name, value) in response.headers.items()
               if name != 'Content-Length']
    return response.content, response.status_code, headers


@app.post("/explain")
def explain():
    return {
        "message": "explain is not supported",
        "details": None
    }
