import json
import os
import requests
import loncel


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    KEY = os.environ.get("KEY")
    try:
        request_key = event["queryStringParameters"]["key"]
        if request_key != KEY:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Unauthorized"}),
            }
    except KeyError:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "Unauthorized"}),
        }

    try:
        unit = event["queryStringParameters"]["unit"]
        total_hours, trip_hours = loncel.getUnitHours(unit)

    except requests.RequestException as e:

        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "totalHours": total_hours,
                "tripHours": trip_hours,
            }
        ),
    }
