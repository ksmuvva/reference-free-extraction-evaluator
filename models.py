from typing import Any, Literal
from pydantic import BaseModel, Field

Status = Literal["PASS", "WARN", "FAIL", "NOT_APPLICABLE", "INDETERMINATE"]

class SchemaResult(BaseModel):
    json_valid: bool = True
    schema_valid: bool
    missing_fields: list[str] = Field(default_factory=list)
    wrong_type_fields: list[str] = Field(default_factory=list)
    unexpected_fields: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)

class OutputClaim(BaseModel):
    claim_id: str
    claim: str
    output_value: Any

class SourceFact(BaseModel):
    fact_id: str
    fact: str
    evidence_questions: list[int | str] = Field(default_factory=list)

class ClaimDecision(BaseModel):
    claim_id: str
    claim: str
    supported: bool
    correct_field: bool
    entity_correct: bool
    contradiction: bool
    matched_source_fact_ids: list[str] = Field(default_factory=list)
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
    faithfulness: float | None
    coverage: float | None
    field_alignment: float | None
    entity_attribution: float | None
    hallucinations: int
    contradictions: int
    wrong_entity_count: int
    status: Status
    issues: list[str] = Field(default_factory=list)

class TranscriptMetrics(BaseModel):
    fields: list[FieldMetrics]
    overall_faithfulness: float | None
    overall_coverage: float | None
    overall_field_alignment: float | None
    overall_entity_attribution: float | None
    overall_score: float | None
    total_hallucinations: int
    total_contradictions: int
    total_wrong_entity: int
    status: Status

class EvaluationReport(BaseModel):
    schema_result: SchemaResult
    evidence: list[EvaluationEvidence]
    metrics: TranscriptMetrics
