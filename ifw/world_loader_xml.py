from __future__ import annotations

import xml.etree.ElementTree as ET


def _required_attr(element: ET.Element, name: str) -> str:
    value = element.get(name)
    if value is None or not value.strip():
        raise ValueError(f"Missing required attribute '{name}' on <{element.tag}>.")
    return value.strip()


def _optional_text(element: ET.Element | None) -> str:
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes"}


def _parse_int(value: str | None, default: int = 0) -> int:
    if value is None or not value.strip():
        return default
    return int(value)


def _parse_classes(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return []
    normalized = value.replace(";", ",").replace("|", ",").replace(" ", ",")
    return [class_name.strip().lower() for class_name in normalized.split(",") if class_name.strip()]


def _parse_id_list(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return []
    normalized = value.replace(";", ",").replace("|", ",").replace(" ", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def _first_attr(element: ET.Element, *names: str) -> str | None:
    for name in names:
        value = element.get(name)
        if value is not None and value.strip():
            return value.strip()
    return None


def _required_attr_any(element: ET.Element, *names: str) -> str:
    value = _first_attr(element, *names)
    if value is None:
        raise ValueError(
            f"Missing required attribute '{' or '.join(names)}' on <{element.tag}>."
        )
    return value
