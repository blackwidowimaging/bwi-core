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

### From the published wheel on GitHub Releases (what Lambdas use)

Add to the consuming repo's `requirements.txt`:

```
bwi-core @ https://github.com/blackwidowimaging/bwi-core/releases/download/v0.2.1/bwi_core-0.2.1-py3-none-any.whl
```

Bump the version twice in the URL when upgrading: once in the tag (`v0.2.1`) and once in the wheel filename (`bwi_core-0.2.1-...`).

No credentials needed — the repo is public.

**Why a wheel URL and not `git+https://...@v0.2.1`?** AWS SAM's `sam build` uses `aws-lambda-builders`, which reads package metadata directly from the source tree. A fresh git clone of a `pyproject.toml`-only package has no `PKG-INFO` file (it's generated during build), so the git-URL form fails with "Unable to find PKG-INFO". A wheel has `METADATA` baked in and works fine.

## Releasing a new version

1. Bump the version in **both** `pyproject.toml` (the `version` field) and `src/bwi_core/__init__.py` (the `__version__` line). They must match.
2. Commit the change.
3. Tag and push:
   ```bash
   git tag v0.2.2
   git push origin main --tags
   ```
4. The `Publish wheel on tag` GitHub Action runs automatically: builds the wheel, creates a GitHub Release for the tag, and attaches `bwi_core-<version>-py3-none-any.whl` and the sdist. Confirm at https://github.com/blackwidowimaging/bwi-core/releases.
5. Update consuming repos' `requirements.txt` to point at the new wheel URL.

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
