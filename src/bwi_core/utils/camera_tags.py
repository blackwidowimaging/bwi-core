"""Canonical CCW ordering for camera ``camera_position`` assignment.

The companion TypeScript implementation lives in
``ums-client/src/components/carousel/cameraTagPosition.ts`` (``rankForCameraTag``).
Keep that copy and this one in sync — they're the same product spec applied at
display time (TS) and at storage time (Python).

Rule: lower rank = earlier slot. Within a base location the priority is
High -> base -> Low, so LFH always ranks before LF, which ranks before LFL.
Roof variants sort after every sided position. Unassigned / unknown tags sort
last so they fall to the tail of the renumber pass.

Typical use: sort a list of cameras by ``rank_for_camera_tag(camera["tag"])`` then
assign ``camera_position = index + 1`` to each.
"""

from typing import Optional, Union

UNASSIGNED_RANK = 9999
ROOF_RANK = 9000
_HIGH_OFFSET = -1
_BASE_OFFSET = 0
_LOW_OFFSET = 1
_TAG_VARIANT_STRIDE = 10

_BASE_POSITIONS_CCW = {
    "Left Front": 1,
    "Left Side": 2,
    "Left Rear": 3,
    "Rear": 4,
    "Right Rear": 5,
    "Right Side": 6,
    "Right Front": 7,
    "Front": 8,
}

_ABBREV_TO_TAG = {
    "LF": "Left Front",
    "LS": "Left Side",
    "LR": "Left Rear",
    "R": "Rear",
    "RR": "Right Rear",
    "RS": "Right Side",
    "RF": "Right Front",
    "F": "Front",
    "T": "Roof",
}


def _strip_letter_suffix(tag: str) -> str:
    """Strip "-letter" sub-position suffixes used by featured-style names ("LF-a")."""
    dash_idx = tag.find("-")
    return tag[:dash_idx] if dash_idx >= 0 else tag


def rank_for_camera_tag(tag: Optional[Union[str, int, float]]) -> int:
    """Return a sortable rank for a camera tag using CCW canonical order.

    Accepts full tag names ("Left Front", "Right Rear High"), abbreviations
    ("LF", "RR"), abbreviations with sub-letter ("LF-a"), and the special values
    "Unassigned" / "N/A" / None / empty. Returns ``UNASSIGNED_RANK`` for anything
    that doesn't resolve to a known base position.
    """
    if tag is None:
        return UNASSIGNED_RANK
    trimmed = str(tag).strip()
    if not trimmed or trimmed in ("Unassigned", "N/A"):
        return UNASSIGNED_RANK

    bare = _strip_letter_suffix(trimmed)

    suffix_offset = _BASE_OFFSET
    if bare.endswith(" High"):
        suffix_offset = _HIGH_OFFSET
        bare = bare[: -len(" High")]
    elif bare.endswith(" Low"):
        suffix_offset = _LOW_OFFSET
        bare = bare[: -len(" Low")]

    expanded = _ABBREV_TO_TAG.get(bare.upper())
    base = expanded if expanded else bare

    if base == "Roof":
        return ROOF_RANK + suffix_offset

    base_position = _BASE_POSITIONS_CCW.get(base)
    if base_position is None:
        return UNASSIGNED_RANK

    return base_position * _TAG_VARIANT_STRIDE + suffix_offset
