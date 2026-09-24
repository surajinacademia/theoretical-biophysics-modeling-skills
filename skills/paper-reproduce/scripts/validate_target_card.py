#!/usr/bin/env python3
"""Compute and validate a reproduce-paper target-card specification hash."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

import yaml


SPECIFICATION_FIELDS = (
    "schema_version",
    "id",
    "route",
    "depth",
    "comparison_strength",
    "variant",
    "sources",
    "target",
    "source_audit",
    "variant_specification",
    "protocol",
)
REVISION_FIELDS = (
    "revision_id",
    "supersedes_revision_id",
    "change_reason",
    "frozen_at",
)
LINEAGE_FIELDS = ("predecessor_card", "predecessor_specification_hash")
ROUTES = {"paper_method", "user_model"}
DEPTHS = {"model_or_method", "claim", "result"}
STRENGTHS = {"qualitative", "quantitative", "not_applicable"}
VARIANTS = {"baseline", "extension", "not_applicable"}
SOURCE_KINDS = {
    "paper",
    "supplement",
    "erratum",
    "repository",
    "dataset",
    "figure",
    "cited_method",
}
TARGET_KINDS = {"method", "claim"}
AUDIT_STATUSES = {
    "reported",
    "inherited",
    "ambiguous",
    "conflicting",
    "missing",
    "not_applicable",
}
MATERIALITIES = {
    "blocking",
    "sensitivity_required",
    "nonmaterial",
    "not_applicable",
}
EXECUTION_STATUSES = {"not_started", "diagnostic", "valid", "partial", "failed"}
INTEGRITY_STATUSES = {"not_started", "valid", "partial", "failed"}
METHODOLOGY_FIDELITIES = {
    "exact",
    "source_backed_reconstruction",
    "known_deviation",
    "incomplete_unknown",
    "not_evaluated",
}

PAPER_VERDICTS = {
    "exact_agreement",
    "quantitative_agreement",
    "qualitative_agreement",
    "disagreement",
    "inconclusive",
    "not_evaluated",
}
USER_VERDICTS = {
    "quantitatively_consistent",
    "qualitatively_consistent",
    "fit_consistent",
    "disagreement",
    "inconclusive",
    "not_evaluated",
}

EXACTNESS_REPRESENTATIONS = {
    "deterministic_exact",
    "finite_precision",
    "digitized",
    "stochastic",
    "not_applicable",
}
SENSITIVITY_ROBUSTNESS = {"robust", "sensitive", "inconclusive"}
PLACEHOLDER_STRINGS = {
    "-",
    "n/a",
    "na",
    "none",
    "not applicable",
    "not_applicable",
    "tbd",
    "to be determined",
    "unknown",
}
VAGUE_RUN_TOKENS = {
    "as needed",
    "as required",
    "as appropriate",
    "many",
    "multiple",
    "further runs",
    "if warranted",
    "several",
    "some",
    "tbd",
    "to be determined",
    "various",
}
NUMBER_WORDS = {
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
}
TERMINAL_EVIDENCE_FIELDS = (
    ("execution", "code_path"),
    ("execution", "code_version_or_hash"),
    ("execution", "configuration"),
    ("execution", "command"),
    ("execution", "environment_summary"),
    ("execution", "raw_data_path"),
    ("evaluation", "local_result"),
    ("evaluation", "uncertainty"),
)


def nonblank_string(value: Any) -> bool:
    """Return true only for a string with meaningful, canonical outer whitespace."""
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def is_placeholder(value: Any) -> bool:
    """Return whether a string is an explicit non-value placeholder."""
    return isinstance(value, str) and value.strip().lower() in PLACEHOLDER_STRINGS


def validate_string_hygiene(value: Any, label: str, errors: list[str]) -> None:
    """Reject empty or outer-whitespace strings throughout a frozen card."""
    if isinstance(value, str):
        if not value.strip():
            errors.append(f"{label} must not be blank or whitespace")
        elif value != value.strip():
            errors.append(f"{label} must not have leading or trailing whitespace")
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            validate_string_hygiene(nested, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            validate_string_hygiene(nested, f"{label}[{index}]", errors)


def is_canonical_sha256(value: Any) -> bool:
    """Return whether value is a canonical sha256: hexadecimal digest."""
    return isinstance(value, str) and bool(
        re.fullmatch(r"sha256:[0-9a-f]{64}", value)
    )


def path_is_within(child: Any, root: Any) -> bool:
    """Check lexical containment without requiring either path to exist."""
    if not nonblank_string(child) or not nonblank_string(root):
        return False
    child_path = Path(os.path.normpath(child))
    root_path = Path(os.path.normpath(root))
    if child_path.is_absolute() != root_path.is_absolute():
        return False
    try:
        child_path.relative_to(root_path)
    except ValueError:
        return False
    return child_path != root_path


def is_concrete_run_description(value: Any) -> bool:
    """Accept a positive count or a concise plan with an explicit count."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value > 0
    if isinstance(value, dict):
        count = value.get("count")
        description = value.get("description")
        return (
            isinstance(count, int)
            and not isinstance(count, bool)
            and count > 0
            and nonblank_string(description)
        )
    if not nonblank_string(value) or is_placeholder(value):
        return False
    lowered = value.lower()
    if any(token in lowered for token in VAGUE_RUN_TOKENS):
        return False
    return bool(re.search(r"\b[1-9]\d*\b", lowered)) or bool(
        set(re.findall(r"[a-z]+", lowered)) & NUMBER_WORDS
    )


def is_exactness_frozen(protocol: dict[str, Any]) -> bool:
    """Accept an explicit declaration or the retained legacy exact-integer form."""
    exactness = protocol.get("exactness")
    if isinstance(exactness, dict):
        deterministic = exactness.get("deterministic") is True
        representation = exactness.get("representation")
        tolerance = exactness.get("tolerance")
        zero_tolerance = (
            representation == "finite_precision"
            and isinstance(tolerance, (int, float))
            and not isinstance(tolerance, bool)
            and tolerance == 0
        )
        return deterministic and (
            representation == "deterministic_exact" or zero_tolerance
        )
    parameters = protocol.get("parameters")
    rule = protocol.get("acceptance_rule")
    return (
        isinstance(parameters, dict)
        and parameters.get("arithmetic") == "exact integer"
        and isinstance(rule, str)
        and "absolute difference 0" in rule.lower()
    )


def validate_exactness_declaration(protocol: dict[str, Any], errors: list[str]) -> None:
    """Validate the optional structured exactness declaration used by new cards."""
    exactness = protocol.get("exactness")
    if exactness is None:
        return
    if not isinstance(exactness, dict):
        errors.append("protocol.exactness must be a mapping when declared")
        return
    for field in ("deterministic", "representation", "tolerance"):
        if field not in exactness:
            errors.append(f"protocol.exactness requires {field}")
    deterministic = exactness.get("deterministic")
    representation = exactness.get("representation")
    tolerance = exactness.get("tolerance")
    if deterministic is not None and not isinstance(deterministic, bool):
        errors.append("protocol.exactness.deterministic must be boolean or null")
    if representation not in EXACTNESS_REPRESENTATIONS:
        errors.append("protocol.exactness has invalid representation")
    if tolerance is not None and (
        isinstance(tolerance, bool)
        or not isinstance(tolerance, (int, float))
        or tolerance < 0
    ):
        errors.append("protocol.exactness.tolerance must be a nonnegative number or null")
    if representation == "deterministic_exact" and deterministic is not True:
        errors.append("deterministic_exact representation requires deterministic true")


def validate_sensitivity_protocol(
    protocol: dict[str, Any],
    sensitivity_items: list[dict[str, Any]],
    terminal_evidence_required: bool,
    verdict: Any,
    errors: list[str],
) -> None:
    """Require each sensitivity-required source gap to have executed coverage."""
    if not sensitivity_items:
        return
    sensitivity = protocol.get("sensitivity")
    if not isinstance(sensitivity, dict):
        errors.append("sensitivity_required gaps require protocol.sensitivity")
        return
    coverage = sensitivity.get("execution_coverage")
    if not isinstance(coverage, list) or not coverage:
        errors.append("sensitivity_required gaps require execution coverage")
        coverage = []
    required_items = {item["item"] for item in sensitivity_items}
    alternatives_by_item = {
        item["item"]: item.get("alternatives", []) for item in sensitivity_items
    }
    covered_items: set[str] = set()
    for index, entry in enumerate(coverage):
        label = f"protocol.sensitivity.execution_coverage[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be a mapping")
            continue
        audit_item = entry.get("audit_item")
        if not nonblank_string(audit_item) or audit_item not in required_items:
            errors.append(f"{label}.audit_item must name a sensitivity-required audit item")
            continue
        if audit_item in covered_items:
            errors.append(f"{label}.audit_item is duplicated")
        covered_items.add(audit_item)
        alternatives = entry.get("alternatives")
        declared_alternatives = alternatives_by_item[audit_item]
        if (
            not isinstance(alternatives, list)
            or not alternatives
            or any(not nonblank_string(item) for item in alternatives)
            or len(alternatives) != len(set(alternatives))
            or set(alternatives) != set(declared_alternatives)
        ):
            errors.append(f"{label}.alternatives must cover the audited alternatives")
        if not is_concrete_run_description(entry.get("required_runs")):
            errors.append(f"{label}.required_runs must be concrete")
        raw_data_path = entry.get("raw_data_path")
        if not nonblank_string(raw_data_path) or is_placeholder(raw_data_path):
            errors.append(f"{label}.raw_data_path must be explicit")
    if covered_items != required_items:
        errors.append("sensitivity execution coverage must cover every sensitivity-required audit item")

    conclusion = sensitivity.get("conclusion")
    if conclusion is None and not terminal_evidence_required:
        return
    if not isinstance(conclusion, dict):
        errors.append("sensitivity_required gaps require a structured conclusion")
        return
    robustness = conclusion.get("robustness")
    if robustness not in SENSITIVITY_ROBUSTNESS:
        errors.append("protocol.sensitivity.conclusion has invalid robustness")
    if not nonblank_string(conclusion.get("statement")):
        errors.append("protocol.sensitivity.conclusion requires a nonblank statement")
    if verdict != "not_evaluated" and robustness != "robust":
        errors.append("a scientific verdict requires a robust sensitivity conclusion")


def load_card(path: Path) -> dict[str, Any]:
    """Load one YAML/JSON target card."""
    with path.open(encoding="utf-8") as handle:
        card = yaml.safe_load(handle)
    if not isinstance(card, dict):
        raise ValueError("target card must be a mapping")
    return card


def specification_payload(card: dict[str, Any]) -> dict[str, Any]:
    """Return frozen scientific fields plus immutable revision identity."""
    missing = [field for field in SPECIFICATION_FIELDS if field not in card]
    if missing:
        raise ValueError(f"missing specification fields: {', '.join(missing)}")
    revision = card.get("specification_revision")
    if not isinstance(revision, dict):
        raise ValueError("specification_revision must be a mapping")
    missing_revision = [field for field in REVISION_FIELDS if field not in revision]
    if missing_revision:
        raise ValueError(f"missing revision fields: {', '.join(missing_revision)}")
    payload = {field: card[field] for field in SPECIFICATION_FIELDS}
    payload["specification_revision"] = {
        field: revision[field] for field in REVISION_FIELDS
    }
    if revision.get("supersedes_revision_id") is not None:
        payload["specification_revision"].update(
            {field: revision.get(field) for field in LINEAGE_FIELDS}
        )
    return payload


def compute_specification_hash(card: dict[str, Any]) -> str:
    """Hash compact, key-sorted, UTF-8 JSON with non-finite numbers rejected."""
    encoded = json.dumps(
        specification_payload(card),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def is_populated(value: Any) -> bool:
    """Return whether a required scalar or collection carries real content."""
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    if isinstance(value, (int, float)):
        return value > 0
    return True


def has_meaningful_content(value: Any) -> bool:
    """Reject containers whose leaves are only null, blank, false, or placeholders."""
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return nonblank_string(value) and not is_placeholder(value)
    if isinstance(value, dict):
        return bool(value) and any(has_meaningful_content(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return bool(value) and any(has_meaningful_content(item) for item in value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    return True


def validate_revision_lineage(
    card: dict[str, Any],
    card_path: Path | None = None,
    ancestry_paths: set[Path] | None = None,
    ancestry_revision_ids: set[str] | None = None,
) -> list[str]:
    """Fully validate an explicitly referenced immutable predecessor-card chain."""
    errors: list[str] = []
    revision = card.get("specification_revision")
    if not isinstance(revision, dict):
        return ["specification_revision must be a mapping"]
    revision_id = revision.get("revision_id")
    supersedes = revision.get("supersedes_revision_id")
    predecessor_card = revision.get("predecessor_card")
    predecessor_hash = revision.get("predecessor_specification_hash")

    seen_paths = set() if ancestry_paths is None else set(ancestry_paths)
    seen_revision_ids = (
        set() if ancestry_revision_ids is None else set(ancestry_revision_ids)
    )
    current_path = card_path.resolve() if card_path is not None else None
    if current_path is not None and current_path in seen_paths:
        errors.append("revision predecessor chain contains a cycle")
    if isinstance(revision_id, str) and revision_id in seen_revision_ids:
        errors.append("revision predecessor chain repeats a revision ID")
    if supersedes == revision_id and supersedes is not None:
        errors.append("a revision cannot supersede itself")
    if supersedes is None:
        if predecessor_card is not None or predecessor_hash is not None:
            errors.append("a first revision cannot declare predecessor metadata")
        return errors

    if not isinstance(predecessor_card, str) or not predecessor_card.strip():
        errors.append("a superseding revision requires predecessor_card")
    if (
        not isinstance(predecessor_hash, str)
        or not predecessor_hash.startswith("sha256:")
        or len(predecessor_hash) != 71
    ):
        errors.append("a superseding revision requires a canonical predecessor hash")
    if errors:
        return errors
    if card_path is None:
        return ["path-aware validation is required for a superseding revision"]

    predecessor_path = Path(predecessor_card)
    if predecessor_path.is_absolute():
        return ["predecessor_card must be relative to the current card directory"]
    card_root = card_path.parent.resolve()
    predecessor_path = (card_root / predecessor_path).resolve()
    try:
        predecessor_path.relative_to(card_root)
    except ValueError:
        return ["predecessor_card cannot escape the current card directory"]
    if predecessor_path in seen_paths or predecessor_path == current_path:
        return ["revision predecessor chain contains a cycle"]
    if not predecessor_path.is_file():
        return [f"predecessor card does not exist: {predecessor_path}"]

    try:
        predecessor = load_card(predecessor_path)
        computed_hash = compute_specification_hash(predecessor)
    except (OSError, TypeError, ValueError) as exc:
        return [f"invalid predecessor card: {exc}"]
    predecessor_revision = predecessor.get("specification_revision")
    if not isinstance(predecessor_revision, dict):
        return ["predecessor specification_revision must be a mapping"]
    if predecessor.get("id") != card.get("id"):
        errors.append("predecessor card belongs to a different target ID")
    if predecessor_revision.get("revision_id") != supersedes:
        errors.append("predecessor revision ID does not match supersedes_revision_id")
    if predecessor_revision.get("specification_hash") != computed_hash:
        errors.append("predecessor stored specification hash is invalid")
    if predecessor_hash != computed_hash:
        errors.append("declared predecessor hash does not match predecessor card")
    nested = validate_card(
        predecessor,
        predecessor_path,
        _ancestry_paths=seen_paths | ({current_path} if current_path else set()),
        _ancestry_revision_ids=seen_revision_ids
        | ({revision_id} if isinstance(revision_id, str) else set()),
    )
    errors.extend(f"predecessor: {error}" for error in nested)
    return errors


def validate_card(
    card: dict[str, Any],
    card_path: Path | None = None,
    *,
    _ancestry_paths: set[Path] | None = None,
    _ancestry_revision_ids: set[str] | None = None,
) -> list[str]:
    """Return cross-field provenance and scientific-label errors."""
    errors: list[str] = []
    validate_string_hygiene(card, "card", errors)
    try:
        expected_hash = compute_specification_hash(card)
    except (TypeError, ValueError) as exc:
        return [str(exc)]

    revision = card.get("specification_revision")
    if not isinstance(revision, dict):
        return ["specification_revision must be a mapping"]
    stored_hash = revision.get("specification_hash")
    if stored_hash != expected_hash:
        errors.append(
            f"specification_hash mismatch: expected {expected_hash}, got {stored_hash!r}"
        )
    for field in ("revision_id", "change_reason", "frozen_at"):
        if not nonblank_string(revision.get(field)):
            errors.append(f"specification_revision.{field} must be set")
    if revision.get("supersedes_revision_id") is not None and not nonblank_string(
        revision.get("supersedes_revision_id")
    ):
        errors.append("specification_revision.supersedes_revision_id must be null or nonblank")
    errors.extend(
        validate_revision_lineage(
            card,
            card_path,
            _ancestry_paths,
            _ancestry_revision_ids,
        )
    )

    if card.get("schema_version") != 1:
        errors.append("unsupported schema_version; expected 1")
    target_id = card.get("id")
    if not isinstance(target_id, str) or not target_id.strip():
        errors.append("target card id must be a nonempty string")

    route = card.get("route")
    depth = card.get("depth")
    strength = card.get("comparison_strength")
    variant = card.get("variant")
    sources = card.get("sources")
    target = card.get("target")
    protocol = card.get("protocol")
    variant_specification = card.get("variant_specification")
    evaluation = card.get("evaluation")
    execution = card.get("execution")
    source_audit = card.get("source_audit")
    if not isinstance(protocol, dict):
        errors.append("protocol must be a mapping")
        protocol = {}
    if not isinstance(variant_specification, dict):
        errors.append("variant_specification must be a mapping")
        variant_specification = {}
    if not isinstance(evaluation, dict):
        errors.append("evaluation must be a mapping")
        evaluation = {}
    if not isinstance(execution, dict):
        errors.append("execution must be a mapping")
        execution = {}
    if not isinstance(source_audit, dict):
        errors.append("source_audit must be a mapping")
        source_audit = {}
    validate_exactness_declaration(protocol, errors)

    source_ids: set[str] = set()
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain at least one authoritative source")
        sources = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be a mapping")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"sources[{index}].id must be a nonempty string")
        elif source_id in source_ids:
            errors.append(f"duplicate source ID: {source_id}")
        else:
            source_ids.add(source_id)
        if source.get("kind") not in SOURCE_KINDS:
            errors.append(f"sources[{index}] has invalid kind")
        identifier = source.get("identifier")
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"sources[{index}].identifier must be a nonempty string")

    def validate_source_refs(refs: Any, label: str) -> None:
        if not isinstance(refs, list) or not refs:
            errors.append(f"{label} must contain at least one source locator")
            return
        for index, reference in enumerate(refs):
            if not isinstance(reference, dict):
                errors.append(f"{label}[{index}] must be a mapping")
                continue
            if reference.get("source_id") not in source_ids:
                errors.append(f"{label}[{index}] references an unknown source ID")
            locator = reference.get("locator")
            if not isinstance(locator, str) or not locator.strip():
                errors.append(f"{label}[{index}].locator must be a nonempty string")

    if not isinstance(target, dict):
        errors.append("target must be a mapping")
        target = {}
    if target.get("kind") not in TARGET_KINDS:
        errors.append(f"unsupported target kind: {target.get('kind')!r}")
    statement = target.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        errors.append("target.statement must be a nonempty neutral statement")
    validate_source_refs(target.get("source_refs"), "target.source_refs")

    verdict = evaluation.get("verdict")
    allowed = PAPER_VERDICTS if route == "paper_method" else USER_VERDICTS
    if route not in ROUTES:
        errors.append(f"unsupported route: {route!r}")
    elif verdict not in allowed:
        errors.append(f"verdict {verdict!r} is invalid for route {route!r}")
    if depth not in DEPTHS:
        errors.append(f"unsupported depth: {depth!r}")
    if strength not in STRENGTHS:
        errors.append(f"unsupported comparison_strength: {strength!r}")
    if variant not in VARIANTS:
        errors.append(f"unsupported variant: {variant!r}")
    authorized_changes = variant_specification.get("authorized_changes")
    if not isinstance(authorized_changes, list):
        errors.append("variant_specification.authorized_changes must be a list")
        authorized_changes = []
    if variant == "baseline" and authorized_changes:
        errors.append("baseline variant cannot contain authorized changes")
    baseline_specification = variant_specification.get("baseline_specification")
    if variant == "baseline" and (
        not nonblank_string(baseline_specification)
        or is_placeholder(baseline_specification)
    ):
        errors.append("baseline variant requires its unchanged specification")
    if variant == "extension":
        if (
            not nonblank_string(baseline_specification)
            or is_placeholder(baseline_specification)
        ):
            errors.append("extension requires a preserved baseline specification")
        if not authorized_changes or any(
            not nonblank_string(item) or is_placeholder(item)
            for item in authorized_changes
        ):
            errors.append("extension requires at least one authorized change")
        isolated_root = variant_specification.get("isolated_output_root")
        if (
            not nonblank_string(isolated_root)
            or is_placeholder(isolated_root)
            or isolated_root in {".", "/"}
        ):
            errors.append("extension requires an isolated output root")
    if (
        variant == "not_applicable"
        and nonblank_string(revision.get("frozen_at"))
    ):
        errors.append("a frozen target requires baseline or extension variant")

    if depth == "model_or_method":
        if target.get("kind") != "method":
            errors.append("Level 1 target kind must be method")
        if verdict != "not_evaluated":
            errors.append("Level 1 must leave paper agreement not_evaluated")
        if strength != "not_applicable":
            errors.append("Level 1 comparison_strength must be not_applicable")
    else:
        if target.get("kind") != "claim":
            errors.append("claim/result target kind must be claim")
        observable = target.get("observable")
        if not isinstance(observable, str) or not observable.strip():
            errors.append("claim/result target observable must be a nonempty string")
        conditions = target.get("conditions")
        if not isinstance(conditions, dict) or not conditions:
            errors.append("claim/result target conditions must be a nonempty mapping")
        if strength == "not_applicable":
            errors.append("claim/result comparison_strength cannot be not_applicable")

    evaluation_mode = protocol.get("evaluation_mode")
    if route == "paper_method" and evaluation_mode != "not_applicable":
        errors.append("paper-method route requires evaluation_mode not_applicable")
    if route == "user_model" and depth == "model_or_method":
        if evaluation_mode != "not_applicable":
            errors.append("Level 1 user-model evaluation_mode must be not_applicable")
    if route == "user_model" and depth in {"claim", "result"}:
        if evaluation_mode not in {"prediction", "fit"}:
            errors.append("user-model claim/result requires prediction or fit mode")
    if evaluation_mode == "prediction":
        calibration = protocol.get("calibration_conditions")
        held_out = protocol.get("evaluation_conditions")
        if not isinstance(calibration, list) or not calibration:
            errors.append("prediction requires nonempty calibration condition IDs")
            calibration = []
        if not isinstance(held_out, list) or not held_out:
            errors.append("prediction requires nonempty evaluation condition IDs")
            held_out = []
        if any(not isinstance(item, str) or not item.strip() for item in calibration):
            errors.append("calibration condition IDs must be nonempty strings")
        if any(not isinstance(item, str) or not item.strip() for item in held_out):
            errors.append("evaluation condition IDs must be nonempty strings")
        if len(calibration) != len(set(calibration)):
            errors.append("calibration condition IDs must be unique")
        if len(held_out) != len(set(held_out)):
            errors.append("evaluation condition IDs must be unique")
        if set(calibration) & set(held_out):
            errors.append("prediction calibration and evaluation conditions must be disjoint")
    if verdict == "quantitatively_consistent" and strength != "quantitative":
        errors.append("quantitatively_consistent requires quantitative comparison")
    if verdict == "qualitatively_consistent" and strength != "qualitative":
        errors.append("qualitatively_consistent requires qualitative comparison")
    if verdict in {"quantitatively_consistent", "qualitatively_consistent"}:
        if evaluation_mode != "prediction":
            errors.append(f"{verdict} requires evaluation_mode prediction")
    if verdict == "fit_consistent" and evaluation_mode != "fit":
        errors.append("fit_consistent requires evaluation_mode fit")
    if evaluation_mode == "fit" and verdict in {
        "quantitatively_consistent",
        "qualitatively_consistent",
    }:
        errors.append("fit mode cannot receive a held-out consistency verdict")
    if verdict in {"exact_agreement", "quantitative_agreement"}:
        if strength != "quantitative":
            errors.append(f"{verdict} requires quantitative comparison")
    if verdict == "exact_agreement" and not is_exactness_frozen(protocol):
        errors.append(
            "exact_agreement requires deterministic exact representation or frozen zero tolerance"
        )
    if verdict == "qualitative_agreement" and strength != "qualitative":
        errors.append("qualitative_agreement requires qualitative comparison")

    status = execution.get("status")
    integrity = evaluation.get("execution_integrity")
    methodology_fidelity = evaluation.get("methodology_fidelity")
    if status not in EXECUTION_STATUSES:
        errors.append(f"unsupported execution status: {status!r}")
    if integrity not in INTEGRITY_STATUSES:
        errors.append(f"unsupported execution_integrity: {integrity!r}")
    if methodology_fidelity not in METHODOLOGY_FIDELITIES:
        errors.append(f"unsupported methodology_fidelity: {methodology_fidelity!r}")
    if verdict != "not_evaluated" and methodology_fidelity == "not_evaluated":
        errors.append("a scientific verdict requires methodology fidelity evaluation")
    if status in {"not_started", "valid", "partial", "failed"}:
        if integrity != status:
            errors.append("evaluation execution_integrity does not match execution status")

    items = source_audit.get("items")
    blocking = False
    sensitivity_items: list[dict[str, Any]] = []
    unresolved_exact_reproduction = False
    if not isinstance(items, list):
        errors.append("source_audit.items must be a list")
        items = []
    if not items:
        errors.append("source_audit.items must contain at least one target-relevant item")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"source_audit.items[{index}] must be a mapping")
            continue
        item_name = item.get("item")
        if not isinstance(item_name, str) or not item_name.strip():
            errors.append(f"source_audit.items[{index}].item must be a nonempty string")
        item_refs = item.get("source_refs")
        validate_source_refs(
            item_refs, f"source_audit.items[{index}].source_refs"
        )
        audit_status = item.get("status")
        materiality = item.get("materiality")
        if audit_status not in AUDIT_STATUSES:
            errors.append(f"source_audit.items[{index}] has invalid status")
        if materiality not in MATERIALITIES:
            errors.append(f"source_audit.items[{index}] has invalid materiality")
        if audit_status in {"reported", "inherited", "not_applicable"}:
            if materiality != "not_applicable":
                errors.append(
                    f"source_audit.items[{index}] resolved status requires not_applicable materiality"
                )
        if audit_status in {"ambiguous", "conflicting", "missing"}:
            if materiality == "not_applicable":
                errors.append(
                    f"source_audit.items[{index}] unresolved status requires gap materiality"
                )
            if not isinstance(item.get("affects_exact_reproduction"), bool):
                errors.append(
                    f"source_audit.items[{index}] unresolved status requires an exact-reproduction effect"
                )
            alternatives = item.get("alternatives")
            if not isinstance(alternatives, list) or not alternatives:
                errors.append(
                    f"source_audit.items[{index}] unresolved status requires documented alternatives"
                )
            resolution = item.get("resolution")
            if not isinstance(resolution, str) or not resolution.strip():
                errors.append(
                    f"source_audit.items[{index}] unresolved status requires a resolution explanation"
                )
            if item.get("affects_exact_reproduction") is True:
                unresolved_exact_reproduction = True
        referenced_ids = (
            {
                reference.get("source_id")
                for reference in item_refs
                if isinstance(reference, dict)
            }
            if isinstance(item_refs, list)
            else set()
        )
        if audit_status == "inherited" and len(referenced_ids) < 2:
            errors.append(
                f"source_audit.items[{index}] inherited status requires delegation and inherited-method sources"
            )
        if audit_status == "conflicting" and len(referenced_ids) < 2:
            errors.append(
                f"source_audit.items[{index}] conflicting status requires at least two sources"
            )
        blocking = blocking or materiality == "blocking"
        if (
            materiality == "sensitivity_required"
            and audit_status in {"ambiguous", "conflicting", "missing"}
            and nonblank_string(item_name)
        ):
            sensitivity_items.append(item)

    if blocking:
        if verdict != "not_evaluated":
            errors.append("blocking gaps require verdict not_evaluated")
        if status in {"valid", "partial"}:
            errors.append("blocking gaps prohibit valid or partial evidence")
    if status in {"diagnostic", "partial", "failed"} and verdict != "not_evaluated":
        errors.append(f"execution status {status} cannot support a scientific verdict")
    if verdict != "not_evaluated":
        if status != "valid" or integrity != "valid":
            errors.append("a scientific verdict requires valid execution and integrity")
    completed_execution = status in {"valid", "partial", "failed"}
    if completed_execution:
        for field in ("sampling_unit", "analysis", "acceptance_rule"):
            if not is_populated(protocol.get(field)):
                errors.append(f"completed execution requires protocol.{field}")
        if not is_concrete_run_description(protocol.get("required_runs")):
            errors.append("completed execution requires a concrete protocol.required_runs")
        if depth in {"claim", "result"} and (
            not isinstance(protocol.get("parameters"), dict)
            or not has_meaningful_content(protocol.get("parameters"))
        ):
            errors.append("completed claim/result execution requires meaningful protocol.parameters")
        if variant == "not_applicable":
            errors.append("completed execution requires baseline or extension variant")

    terminal_evidence_required = completed_execution or verdict != "not_evaluated"
    if terminal_evidence_required:
        for section, field in TERMINAL_EVIDENCE_FIELDS:
            section_data = execution if section == "execution" else evaluation
            value = section_data.get(field)
            if field in {
                "code_path",
                "command",
                "environment_summary",
                "raw_data_path",
            }:
                populated = nonblank_string(value) and not is_placeholder(value)
            elif field in {"configuration", "local_result", "uncertainty"}:
                populated = has_meaningful_content(value)
            else:
                populated = is_populated(value)
            if not populated:
                errors.append(f"valid execution requires {section}.{field}")
        if not is_canonical_sha256(execution.get("code_version_or_hash")):
            errors.append("valid execution requires execution.code_version_or_hash sha256")
    validate_sensitivity_protocol(
        protocol,
        sensitivity_items,
        terminal_evidence_required,
        verdict,
        errors,
    )
    if variant == "extension" and terminal_evidence_required:
        isolated_root = variant_specification.get("isolated_output_root")
        raw_paths = [("execution.raw_data_path", execution.get("raw_data_path"))]
        sensitivity = protocol.get("sensitivity")
        if isinstance(sensitivity, dict):
            coverage = sensitivity.get("execution_coverage")
            if isinstance(coverage, list):
                raw_paths.extend(
                    (
                        f"protocol.sensitivity.execution_coverage[{index}].raw_data_path",
                        entry.get("raw_data_path"),
                    )
                    for index, entry in enumerate(coverage)
                    if isinstance(entry, dict)
                )
        for label, raw_path in raw_paths:
            if nonblank_string(raw_path) and not path_is_within(raw_path, isolated_root):
                errors.append(f"{label} must be contained under isolated_output_root")
    if methodology_fidelity == "exact" and unresolved_exact_reproduction:
        errors.append(
            "methodology_fidelity exact is prohibited by unresolved exact-reproduction gaps"
        )

    execution_revision = execution.get("governing_revision_id")
    execution_hash = execution.get("governing_specification_hash")
    evaluation_revision = evaluation.get("governing_revision_id")
    if execution_revision is not None and execution_revision != revision.get("revision_id"):
        errors.append("execution governing revision does not match")
    if execution_hash is not None and execution_hash != expected_hash:
        errors.append("execution governing specification hash does not match")
    if evaluation_revision is not None and evaluation_revision != revision.get("revision_id"):
        errors.append("evaluation governing revision does not match")
    if status in {"valid", "partial", "failed"}:
        if execution_revision is None:
            errors.append("completed execution requires a governing revision")
        if execution_hash is None:
            errors.append("completed execution requires a governing specification hash")
    if verdict != "not_evaluated":
        if evaluation_revision is None:
            errors.append("a scientific verdict requires a governing revision")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("card", type=Path)
    parser.add_argument(
        "--compute",
        action="store_true",
        help="print the canonical hash without checking the stored value",
    )
    args = parser.parse_args()
    card = load_card(args.card)
    if args.compute:
        print(compute_specification_hash(card))
        return 0
    errors = validate_card(card, args.card)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
