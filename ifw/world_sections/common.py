from __future__ import annotations

import xml.etree.ElementTree as ET

from ..world_loader_xml import _parse_int


def first_child(element: ET.Element, *tags: str) -> ET.Element | None:
    for tag in tags:
        child = element.find(tag)
        if child is not None:
            return child
    return None


def optional_int_attr(element: ET.Element, *names: str) -> int | None:
    for name in names:
        if name in element.attrib:
            return _parse_int(element.get(name))
    return None


def optional_present_attr(element: ET.Element, *names: str) -> str | None:
    for name in names:
        if name in element.attrib:
            return (element.get(name) or "").strip()
    return None
