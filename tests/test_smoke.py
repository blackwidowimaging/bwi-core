"""Minimal smoke tests verifying the package imports and exposes the expected names."""


def test_package_version():
    import bwi_core
    assert bwi_core.__version__


def test_imports():
    from bwi_core.services.dynamo import DynamoConnection
    from bwi_core.services.cognito import CognitoConnection
    from bwi_core.services.deserialize_dynamo import deserialize_dynamo
    from bwi_core.services.mqtt_ssm import publish_payload_to_system, resolve_active_unit_index
    from bwi_core.models.api_response import APIResponse
    from bwi_core.models.request_event import RequestEvent
    from bwi_core.utils.logger import setup_logger

    assert DynamoConnection
    assert CognitoConnection
    assert deserialize_dynamo
    assert publish_payload_to_system
    assert resolve_active_unit_index
    assert APIResponse
    assert RequestEvent
    assert setup_logger


def test_api_response_shapes():
    from bwi_core.models.api_response import APIResponse
    import json

    not_found = APIResponse.not_found("nope")
    assert not_found["statusCode"] == 404
    assert json.loads(not_found["body"]) == {"error": "nope"}

    success = APIResponse.success("hi")
    assert success["statusCode"] == 200
    assert json.loads(success["body"]) == {"message": "hi"}


def test_build_update_components():
    from bwi_core.services.dynamo import DynamoConnection

    parts = DynamoConnection.build_update_components(
        attributes={"name": "alice", "address.city": "NYC"},
        remove_paths=["nickname"],
    )
    assert "SET" in parts["UpdateExpression"]
    assert "REMOVE" in parts["UpdateExpression"]
    assert ":v0" in parts["ExpressionAttributeValues"]
    assert ":v1" in parts["ExpressionAttributeValues"]
