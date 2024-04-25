import json
import requests
import os
from requests_aws4auth import AWS4Auth  # pip install requests-aws4auth #type: ignore

## get env variables

API_KEY = os.environ.get("LONCEL_API_KEY")
USER = os.environ.get("LONCEL_API_USER")
PWD = os.environ.get("LONCEL_API_PWD")


# access the session with config
def getSession():
    CONFIG = {
        "API_KEY": API_KEY,
        "USER": USER,
        "PWD": PWD,
        "REGION": "ap-southeast-2",
    }

    headers = {"host": "api.loncel.com", "x-api-key": CONFIG["API_KEY"]}

    data = (
        """{"user":"%s", "password": "%s", "region": "%s", "includeCredentials": true}"""
        % (CONFIG["USER"], CONFIG["PWD"], CONFIG["REGION"])
    )
    response = requests.post(
        "https://api.frostsmart.com/v1/user/login", data=data, headers=headers
    )
    return response.json()


def auth():
    # 1. Get the session
    session = getSession()
    service = "execute-api"
    # 2. Auth to sign requests
    auth = AWS4Auth(
        session["credentials"]["accessKeyId"],
        session["credentials"]["secretAccessKey"],
        "ap-southeast-2",
        service,
        session_token=session["credentials"]["sessionToken"],
    )
    return auth


def getUnitHours(unit: str):
    headers = {"host": "api.frostsmart.com", "x-api-key": API_KEY}
    data = (
        """{"user":"%s", "password": "%s", "region": "%s", "includeCredentials": true}"""
        % (USER, PWD, "ap-southeast-2")
    )
    response = requests.post(
        "https://api.frostsmart.com/v1/user/login", data=data, headers=headers
    )
    session = response.json()

    # 2. Auth to sign requests
    auth = AWS4Auth(
        session["credentials"]["accessKeyId"],
        session["credentials"]["secretAccessKey"],
        "ap-southeast-2",
        "execute-api",
        session_token=session["credentials"]["sessionToken"],
    )

    q = {
        "startRelative": {"value": "1", "unit": "weeks"},
        "metrics": [
            {
                "name": "loncel.fan.engine.total.value",
                "filter": {"unit": unit},
                "aggregator": {
                    "name": "last",
                    "sampling": {"value": 1, "unit": "days"},
                },
            },
            {
                "name": "loncel.fan.engine.trip.value",
                "filter": {"unit": unit},
                "aggregator": {"name": "max", "sampling": {"value": 1, "unit": "days"}},
            },
        ],
    }
    ## convert q into json string
    q = json.dumps(q)

    response = requests.post(
        "https://api.frostsmart.com/v1/metrics/query",
        data=q,
        headers=headers,
        auth=auth,
    )
    raw_response = response.json()
    total = 0
    trip = 0
    res = raw_response["queries"]
    for q in res:
        for r in q["results"]:
            print("r:", r)
            if r["name"] == "loncel.fan.engine.total.value":
                total = r["values"][-1][1]
            if r["name"] == "loncel.fan.engine.trip.value":
                trip = r["values"][-1][1]

    return total, trip
