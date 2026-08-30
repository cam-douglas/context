"""Lossless Ableton Live Set (.als) ↔ JSON tree.

An .als file is gzip-compressed XML. This codec keeps element order, attributes,
and empty children so a parse → JSON → write round-trip preserves session nodes
the merger does not touch.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ALS_JSON_VERSION = 1


def _element_to_node(element: ET.Element) -> dict[str, Any]:
    node: dict[str, Any] = {"tag": element.tag}
    if element.attrib:
        node["attrib"] = dict(element.attrib)
    text = (element.text or "").strip()
    if text:
        node["text"] = text
    children = [_element_to_node(child) for child in list(element)]
    if children:
        node["children"] = children
    return node


def _node_to_element(node: dict[str, Any]) -> ET.Element:
    if not isinstance(node, dict) or "tag" not in node:
        raise ValueError("als-json node must be an object with tag")
    element = ET.Element(str(node["tag"]), {str(key): str(value) for key, value in (node.get("attrib") or {}).items()})
    if node.get("text"):
        element.text = str(node["text"])
    for child in node.get("children") or []:
        element.append(_node_to_element(child))
    return element


def als_to_tree(path: str | Path) -> ET.Element:
    source = Path(path)
    raw = source.read_bytes()
    if len(raw) >= 2 and raw[0] == 0x1F and raw[1] == 0x8B:
        raw = gzip.decompress(raw)
    return ET.fromstring(raw)


def tree_to_als_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="\t")
    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
    return gzip.compress(xml)


def tree_to_json(root: ET.Element) -> dict[str, Any]:
    return {
        "als_json_version": ALS_JSON_VERSION,
        "root": _element_to_node(root),
    }


def json_to_tree(payload: dict[str, Any]) -> ET.Element:
    if not isinstance(payload, dict) or "root" not in payload:
        raise ValueError("als-json payload must contain root")
    return _node_to_element(payload["root"])


def parse_als(path: str | Path) -> dict[str, Any]:
    root = als_to_tree(path)
    return tree_to_json(root)


def write_als(path: str | Path, payload: dict[str, Any] | ET.Element) -> str:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    root = payload if isinstance(payload, ET.Element) else json_to_tree(payload)
    dest.write_bytes(tree_to_als_bytes(root))
    return str(dest)


def write_als_json(path: str | Path, payload: dict[str, Any]) -> str:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(dest)


def attr(element: ET.Element | None, name: str, default: str = "") -> str:
    if element is None:
        return default
    return element.attrib.get(name, default)


def child(element: ET.Element | None, tag: str) -> ET.Element | None:
    if element is None:
        return None
    return element.find(tag)


def ensure_child(element: ET.Element, tag: str) -> ET.Element:
    found = element.find(tag)
    if found is not None:
        return found
    created = ET.SubElement(element, tag)
    return created


def set_value(element: ET.Element | None, value: Any) -> None:
    if element is None:
        return
    element.set("Value", str(value))


def iter_ids(root: ET.Element) -> list[int]:
    values: list[int] = []
    for element in root.iter():
        raw = element.attrib.get("Id")
        if raw is None:
            continue
        try:
            values.append(int(raw))
        except ValueError:
            continue
    return values


def remap_ids(subtree: ET.Element, used: set[int]) -> int:
    mapping: dict[int, int] = {}
    next_id = (max(used) + 1) if used else 1

    def take(old: int) -> int:
        nonlocal next_id
        if old not in mapping:
            while next_id in used or next_id in mapping.values():
                next_id += 1
            mapping[old] = next_id
            used.add(next_id)
            next_id += 1
        return mapping[old]

    for element in subtree.iter():
        raw = element.attrib.get("Id")
        if raw is None:
            continue
        try:
            old = int(raw)
        except ValueError:
            continue
        element.set("Id", str(take(old)))
    return next_id
