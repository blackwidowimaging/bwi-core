import json

class APIResponse:
    CORS_HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    @staticmethod
    def ok():
        return {
            "statusCode": 200,
            "headers": APIResponse.CORS_HEADERS
        }

    @staticmethod
    def error():
        return {
            "statusCode": 500,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({"error": "Internal server error"})
        }

    @staticmethod
    def unauthorized():
        return {
            "statusCode": 401,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({"error": "Unauthorized"})
        }

    @staticmethod
    def incomplete():
        return {
            "statusCode": 400,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({"error": "Bad request - incomplete data"})
        }

    @staticmethod
    def result(body, status_code=200):
        return {
            "statusCode": status_code,
            "headers": APIResponse.CORS_HEADERS,
            "body": body
        }

    @staticmethod
    def success(message="Success", status_code=200):
        return {
            "statusCode": status_code,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({"message": message})
        }

    @staticmethod
    def locked(body, status_code=423):
        return {
            "statusCode": status_code,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({'message': body})
        }

    @staticmethod
    def error_with_message(message):
        return {
            "statusCode": 500,
            "body": json.dumps({"error": message}),
            "headers": APIResponse.CORS_HEADERS
        }

    @staticmethod
    def not_found(message="Resource not found"):
        return {
            "statusCode": 404,
            "headers": APIResponse.CORS_HEADERS,
            "body": json.dumps({"error": message})
        }
