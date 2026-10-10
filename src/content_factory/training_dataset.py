from __future__ import annotations

from typing import Any


def build_sft_examples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project accepted/editorially finalized ExperienceRecords into SFT rows."""
    examples = []
    for record in records:
        decision = str(record.get("decision") or "").upper()
        if decision not in {"ACCEPT", "EDIT"}:
            continue
        prompt = record.get("prompt")
        if not isinstance(prompt, (dict, str)):
            continue
        completion = record.get("final") if decision == "EDIT" else record.get("generated")
        if completion is None:
            completion = record.get("generated")
        if completion is None:
            continue
        examples.append({
            "example_id": str(record.get("example_id") or ""),
            "format": "sft",
            "prompt": prompt,
            "completion": completion,
            "context": record.get("context") if isinstance(record.get("context"), dict) else {},
            "qc": record.get("qc") if isinstance(record.get("qc"), dict) else {},
            "provenance": record.get("provenance") if isinstance(record.get("provenance"), dict) else {},
        })
    return examples


def build_preference_examples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project only explicit chosen/rejected pairs into preference rows."""
    examples = []
    for record in records:
        prompt = record.get("prompt")
        preference = record.get("preference")
        if not isinstance(prompt, (dict, str)) or not isinstance(preference, dict):
            continue
        chosen = preference.get("chosen")
        rejected = preference.get("rejected")
        if chosen is None or rejected is None:
            continue
        examples.append({
            "example_id": str(record.get("example_id") or ""),
            "format": "preference",
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
            "context": record.get("context") if isinstance(record.get("context"), dict) else {},
            "provenance": record.get("provenance") if isinstance(record.get("provenance"), dict) else {},
        })
    return examples
