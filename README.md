# bwi-core

Shared Python utilities for BWI Lambda services. Owns the helpers that used to live in `dynamo-api/layers/common/` so that `dynamo-api`, `assetDelivery`, and any future Python services can all use the same code instead of each maintaining their own copy.

## What's in here

- `bwi_core.services.dynamo` — `DynamoConnection` class with `update_attributes()` and update-expression building
- `bwi_core.services.cognito` — `CognitoConnection` for user pool admin operations
- `bwi_core.services.mqtt_ssm` — Publish MQTT payloads to a unit by running `mosquitto_pub` over SSM
- `bwi_core.services.deserialize_dynamo` — Convert raw DynamoDB types into normal Python types
- `bwi_core.models.api_response` — `APIResponse` static helpers for Lambda HTTP responses (with CORS headers)
- `bwi_core.models.request_event` — `RequestEvent` wrapper around the Lambda event dict
- `bwi_core.utils.logger` — `setup_logger(service_name)` for consistent logging

## Naming

| Use | Value |
| --- | --- |
| GitHub repo | `bwi-core` |
| Install name | `bwi-core` |
| Import name | `bwi_core` |

So in code: `from bwi_core.services.dynamo import DynamoConnection`.

## Installing

### From this local directory (for development)

In the consuming repo's virtualenv:

```bash
pip install -e /Users/thomasviles/bwi-stack/bwi-core
```

The `-e` flag means "editable" — changes you make in `bwi-core` are picked up immediately without reinstalling.

### From the public GitHub repo (what Lambdas will use)

Add to the consuming repo's `requirements.txt`:

```
bwi-core @ git+https://github.com/blackwidowimaging/bwi-core.git@v0.2.0
```

Replace `v0.2.0` with whichever tag you want to pin to.

No credentials needed — the repo is public.

## Releasing a new version

1. Edit `pyproject.toml`, bump the `version` field (e.g. `0.1.0` → `0.1.1` for a fix, `0.2.0` for new features).
2. Commit the change.
3. Tag and push:
   ```bash
   git tag v0.1.1
   git push origin main --tags
   ```
4. Update consuming repos' `requirements.txt` to point at the new tag.

Use semantic versioning loosely:
- Patch (`0.1.0` → `0.1.1`) — bug fix, no API change.
- Minor (`0.1.0` → `0.2.0`) — added stuff, didn't break anything.
- Major (`0.1.0` → `1.0.0`) — broke an existing API.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Building a wheel manually

If you ever need an actual `.whl` file (you usually won't — pip-from-git is fine):

```bash
pip install build
python -m build
# Output: dist/bwi_core-<version>-py3-none-any.whl
```

## Required environment variables

Some helpers read environment variables. The consuming Lambda's SAM template must set these (typically with different values per stage).

| Variable | Used by | Required? | Notes |
| --- | --- | --- | --- |
| `COGNITO_USER_POOL_ID` | `CognitoConnection` | yes (when used) | Per-environment user pool ID |
| `MQTT_BROKER` | `publish_payload_to_system` | yes (when used) | MQTT broker host/IP |
| `MQTT_USER` | `publish_payload_to_system` | yes (when used) | MQTT username |
| `MQTT_PASS` | `publish_payload_to_system` | yes (when used) | MQTT password |
| `MQTT_TOPIC` | `publish_payload_to_system` | yes (when used) | MQTT topic |
| `MQTT_PORT` | `publish_payload_to_system` | optional | Defaults to `1883` |

Missing required env vars cause a `RuntimeError` at call time — by design, so misconfiguration fails loudly instead of silently using wrong defaults.
