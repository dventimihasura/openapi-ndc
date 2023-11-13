import json

queryRequest = json.load(open("relationships.json"))


def url(x):
    return f'{scheme(x)}://{host(x)}:{port(x)}{path(x)}{query(x)}'


def scheme(x):
    return 'http'


def host(x):
    return 'localhost'


def port(x):
    return '8080'


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
