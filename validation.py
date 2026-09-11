from collections.abc import Iterable
from typing import Any
from config import OUTPUT_SCHEMA
from models import ClaimDecision, OutputClaim, SchemaResult, SourceFact, SourceFactDecision

class JudgeContractError(ValueError):
    pass

def validate_output_schema(actual_output: Any) -> SchemaResult:
    if not isinstance(actual_output, dict):
        return SchemaResult(schema_valid=False, issues=["Structured output must be a JSON object."])
    missing = [name for name in OUTPUT_SCHEMA if name not in actual_output]
    wrong_types = [name for name, expected_type in OUTPUT_SCHEMA.items() if name in actual_output and not isinstance(actual_output[name], expected_type)]
    unexpected = [name for name in actual_output if name not in OUTPUT_SCHEMA]
    issues = []
    if missing: issues.append(f"Missing required fields: {', '.join(missing)}")
    if wrong_types: issues.append(f"Wrong field types: {', '.join(wrong_types)}")
    if unexpected: issues.append(f"Unexpected fields: {', '.join(unexpected)}")
    return SchemaResult(schema_valid=not missing and not wrong_types, missing_fields=missing, wrong_type_fields=wrong_types, unexpected_fields=unexpected, issues=issues)

def _index_unique(items: Iterable[Any], id_attr: str, label: str) -> dict[str, Any]:
    indexed = {}
    for item in items:
        item_id = getattr(item, id_attr)
        if item_id in indexed:
            raise JudgeContractError(f"Duplicate {label} id returned: {item_id}")
        indexed[item_id] = item
    return indexed

def validate_claim_decisions(expected_claims: list[OutputClaim], returned: list[ClaimDecision]) -> None:
    expected = _index_unique(expected_claims, "claim_id", "input claim")
    actual = _index_unique(returned, "claim_id", "claim decision")
    if set(expected) != set(actual):
        raise JudgeContractError(f"Judge claim ids do not match input; missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
    for claim_id, original in expected.items():
        if actual[claim_id].claim != original.claim:
            raise JudgeContractError(f"Judge altered claim text for {claim_id}: {actual[claim_id].claim!r}")

def validate_source_fact_decisions(expected_facts: list[SourceFact], returned: list[SourceFactDecision]) -> None:
    expected = _index_unique(expected_facts, "fact_id", "source fact")
    actual = _index_unique(returned, "fact_id", "source fact decision")
    if set(expected) != set(actual):
        raise JudgeContractError(f"Judge source fact ids do not match inventory; missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
    for fact_id, original in expected.items():
        if actual[fact_id].fact != original.fact:
            raise JudgeContractError(f"Judge altered source fact text for {fact_id}: {actual[fact_id].fact!r}")

def validate_cross_references(claims: list[ClaimDecision], facts: list[SourceFact]) -> None:
    valid_fact_ids = {fact.fact_id for fact in facts}
    for claim in claims:
        unknown = sorted(set(claim.matched_source_fact_ids) - valid_fact_ids)
        if unknown:
            raise JudgeContractError(f"Claim {claim.claim_id} references unknown source facts: {unknown}")
        if claim.supported and not claim.matched_source_fact_ids:
            raise JudgeContractError(f"Supported claim {claim.claim_id} has no matched_source_fact_ids")
