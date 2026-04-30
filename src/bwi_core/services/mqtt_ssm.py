import json
import os
from typing import Any, Dict, Optional

import boto3


def _mqtt_command(payload: Dict[str, Any]) -> str:
    broker = os.getenv("MQTT_BROKER", "10.2.1.1")
    port = int(os.getenv("MQTT_PORT", "1883"))
    user = os.getenv("MQTT_USER", "bwuser")
    password = os.getenv("MQTT_PASS", "bw2023")
    topic = os.getenv("MQTT_TOPIC", "event")

    mqtt_message = json.dumps(payload).replace('"', '\\"')
    return (
        f'mosquitto_pub -h {broker} -p {port} '
        f'-u {user} -P {password} '
        f'-t {topic} -m "{mqtt_message}"'
    )


def publish_payload_to_system(
    payload: Dict[str, Any],
    system_code: str,
    active_unit_index: str = "U01",
    ssm_client=None,
    timeout_seconds: int = 30,
    logger=None,
) -> Dict[str, Any]:
    """
    Publish an MQTT payload by executing mosquitto_pub on the target managed node.
    Target preference is `<system_code><active_unit_index>`, then `<system_code>`.
    """
    ssm = ssm_client or boto3.client("ssm")
    target_names = [f"{system_code}{active_unit_index}", system_code]

    try:
        instances = ssm.describe_instance_information()["InstanceInformationList"]
        match = next((i for i in instances if i.get("Name") in target_names), None)

        if not match:
            if logger:
                logger.warning(
                    "No SSM instance found for system_code=%s active_unit_index=%s target_names=%s",
                    system_code,
                    active_unit_index,
                    target_names,
                )
            return {"ok": False, "reason": "instance_not_found", "target_names": target_names}

        instance_id = match["InstanceId"]
        command = _mqtt_command(payload)
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [command]},
            TimeoutSeconds=timeout_seconds,
        )

        return {
            "ok": True,
            "instance_id": instance_id,
            "instance_name": match.get("Name"),
            "target_names": target_names,
            "command_id": response.get("Command", {}).get("CommandId"),
        }
    except Exception as ex:
        if logger:
            logger.warning(
                "Failed MQTT publish for system_code=%s active_unit_index=%s error=%s",
                system_code,
                active_unit_index,
                str(ex),
            )
        return {"ok": False, "reason": "exception", "error": str(ex), "target_names": target_names}


def resolve_active_unit_index(
    system_connection,
    system_code: str,
    request_active_unit_index: Optional[str] = None,
    default_active_unit_index: str = "U01",
    logger=None,
) -> str:
    """
    Resolve active unit index by preferring the request value and then system record.
    System records are keyed as (systemCode, unitIndex='U01').
    """
    if request_active_unit_index:
        return request_active_unit_index

    try:
        response = system_connection.dynamo_table.get_item(
            Key={"systemCode": system_code, "unitIndex": "U01"}
        )
        active_from_record = response.get("Item", {}).get("activeUnitIndex")
        return active_from_record or default_active_unit_index
    except Exception as ex:
        if logger:
            logger.warning(
                "Could not resolve activeUnitIndex from system record for system_code=%s error=%s",
                system_code,
                str(ex),
            )
        return default_active_unit_index
