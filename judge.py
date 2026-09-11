"""DSPy semantic components.

Lazy initialization lets deterministic tests run without an API key or DSPy runtime.
"""
import json
from typing import Protocol
from config import FIELD_DEFINITIONS, JUDGE_MODEL
from models import ClaimDecision, EvaluationEvidence, OutputClaim, SourceFact, SourceFactDecision

class SemanticJudge(Protocol):
    def decompose(self, field: str, value: str) -> list[OutputClaim]: ...
    def inventory_source_facts(self, source: dict, field: str) -> list[SourceFact]: ...
    def verify(self, source: dict, field: str, value, claims: list[OutputClaim], source_facts: list[SourceFact]) -> EvaluationEvidence: ...

def _dspy():
    import dspy
    dspy.configure(lm=dspy.LM(JUDGE_MODEL))
    return dspy

class DspySemanticJudge:
    def __init__(self) -> None:
        dspy = _dspy()
        class NarrativeClaimDecomposition(dspy.Signature):
            """Split one existing narrative output value into atomic semantic claims. Preserve meaning; do not add, correct, or infer information."""
            field_name: str = dspy.InputField()
            field_definition: str = dspy.InputField()
            actual_field_value: str = dspy.InputField()
            claims: list[OutputClaim] = dspy.OutputField()
        class SourceFactInventory(dspy.Signature):
            """Identify material source facts for one destination field from the ENTIRE source interview. Do not inspect production output."""
            source_json: str = dspy.InputField()
            field_name: str = dspy.InputField()
            field_definition: str = dspy.InputField()
            facts: list[SourceFact] = dspy.OutputField()
        class EvidenceVerification(dspy.Signature):
            """Verify fixed output claims against a fixed source-fact inventory. Return exactly one decision per supplied claim/fact and do not rewrite IDs or text."""
            source_json: str = dspy.InputField()
            field_name: str = dspy.InputField()
            field_definition: str = dspy.InputField()
            actual_field_value_json: str = dspy.InputField()
            output_claims_json: str = dspy.InputField()
            source_facts_json: str = dspy.InputField()
            claim_decisions: list[ClaimDecision] = dspy.OutputField()
            fact_decisions: list[SourceFactDecision] = dspy.OutputField()
            issues: list[str] = dspy.OutputField()
        self._decomposer = dspy.Predict(NarrativeClaimDecomposition)
        self._inventory = dspy.Predict(SourceFactInventory)
        self._verifier = dspy.Predict(EvidenceVerification)

    def decompose(self, field: str, value: str) -> list[OutputClaim]:
        return self._decomposer(field_name=field, field_definition=FIELD_DEFINITIONS.get(field, field), actual_field_value=value).claims

    def inventory_source_facts(self, source: dict, field: str) -> list[SourceFact]:
        response = self._inventory(source_json=json.dumps(source, ensure_ascii=False), field_name=field, field_definition=FIELD_DEFINITIONS.get(field, field))
        return [SourceFact(fact_id=f"{field}:source:{i}", fact=fact.fact.strip(), evidence_questions=fact.evidence_questions) for i, fact in enumerate(response.facts) if fact.fact.strip()]

    def verify(self, source: dict, field: str, value, claims: list[OutputClaim], source_facts: list[SourceFact]) -> EvaluationEvidence:
        response = self._verifier(
            source_json=json.dumps(source, ensure_ascii=False),
            field_name=field,
            field_definition=FIELD_DEFINITIONS.get(field, field),
            actual_field_value_json=json.dumps(value, ensure_ascii=False),
            output_claims_json=json.dumps([c.model_dump(mode="json") for c in claims], ensure_ascii=False),
            source_facts_json=json.dumps([f.model_dump(mode="json") for f in source_facts], ensure_ascii=False),
        )
        return EvaluationEvidence(field=field, output_value=value, output_claims=response.claim_decisions, source_facts=response.fact_decisions, issues=response.issues)
