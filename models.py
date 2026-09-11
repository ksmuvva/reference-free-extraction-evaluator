from typing import Any
from pydantic import BaseModel, Field


class OutputClaim(BaseModel):
    claim_id: str
    claim: str
    output_value: Any


class ClaimDecision(BaseModel):
    claim_id: str
    claim: str
    supported: bool
    correct_field: bool
    entity_correct: bool
    contradiction: bool
    evidence_questions: list[int | str] = Field(default_factory=list)


class SourceFactDecision(BaseModel):
    fact_id: str
    fact: str
    captured: bool
    evidence_questions: list[int | str] = Field(default_factory=list)


class EvaluationEvidence(BaseModel):
    field: str
    output_value: Any
    output_claims: list[ClaimDecision] = Field(default_factory=list)
    source_facts: list[SourceFactDecision] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class FieldMetrics(BaseModel):
    field: str
    faithfulness: float
    coverage: float
    field_alignment: float
    entity_attribution: float
    hallucinations: int
    contradictions: int
    status: str
    issues: list[str] = Field(default_factory=list)


class TranscriptMetrics(BaseModel):
    fields: list[FieldMetrics]
    overall_faithfulness: float
    overall_coverage: float
    overall_field_alignment: float
    overall_entity_attribution: float
    overall_score: float
    total_hallucinations: int
    total_contradictions: int
    status: str
