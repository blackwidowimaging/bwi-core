from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal


def deserialize_dynamo(data, serializer=TypeDeserializer()):
    if isinstance(data, list):
        return [deserialize_dynamo(value) for value in data]

    if isinstance(data, dict):
        try:
            deserialized = serializer.deserialize(data)
            if isinstance(deserialized, Decimal):
                # If it's a whole number, cast to int
                if deserialized % 1 == 0:
                    return int(deserialized)
                return float(deserialized)
            return deserialized
        except TypeError:
            return {key: deserialize_dynamo(value) for key, value in data.items()}

    if isinstance(data, Decimal):
        if data % 1 == 0:
            return int(data)
        return float(data)

    return data
