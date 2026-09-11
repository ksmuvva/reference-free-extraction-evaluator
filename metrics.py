from statistics import mean
from config import PASS_COVERAGE, PASS_FIELD_ALIGNMENT, WARN_COVERAGE, WARN_FIELD_ALIGNMENT
from models import EvaluationEvidence, FieldMetrics, TranscriptMetrics

def _ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 4)

def calculate_field_metrics(evidence: EvaluationEvidence) -> FieldMetrics:
    claims, facts = evidence.output_claims, evidence.source_facts
    faithfulness = _ratio(sum(c.supported for c in claims), len(claims))
    coverage = _ratio(sum(f.captured for f in facts), len(facts))
    field_alignment = _ratio(sum(c.correct_field for c in claims), len(claims))
    entity_attribution = _ratio(sum(c.entity_correct for c in claims), len(claims))
    hallucinations = sum(not c.supported for c in claims)
    contradictions = sum(c.contradiction for c in claims)
    wrong_entity_count = sum(not c.entity_correct for c in claims)
    issues = list(evidence.issues)
    if not claims and not facts:
        status = "NOT_APPLICABLE"
    elif not claims and facts:
        coverage = 0.0
        status = "FAIL"
        issues.append("Relevant source facts exist but the output field is empty.")
    elif hallucinations or contradictions or wrong_entity_count:
        status = "FAIL"
    elif coverage is not None and coverage < WARN_COVERAGE:
        status = "FAIL"
    elif field_alignment is not None and field_alignment < WARN_FIELD_ALIGNMENT:
        status = "FAIL"
    elif (coverage is not None and coverage < PASS_COVERAGE) or (field_alignment is not None and field_alignment < PASS_FIELD_ALIGNMENT):
        status = "WARN"
    else:
        status = "PASS"
    return FieldMetrics(field=evidence.field, faithfulness=faithfulness, coverage=coverage, field_alignment=field_alignment, entity_attribution=entity_attribution, hallucinations=hallucinations, contradictions=contradictions, wrong_entity_count=wrong_entity_count, status=status, issues=issues)

def _mean_applicable(values: list[float | None]) -> float | None:
    applicable = [v for v in values if v is not None]
    return round(mean(applicable), 4) if applicable else None

def calculate_transcript_metrics(fields: list[FieldMetrics]) -> TranscriptMetrics:
    if not fields:
        return TranscriptMetrics(fields=[], overall_faithfulness=None, overall_coverage=None, overall_field_alignment=None, overall_entity_attribution=None, overall_score=None, total_hallucinations=0, total_contradictions=0, total_wrong_entity=0, status="INDETERMINATE")
    overall_faithfulness = _mean_applicable([f.faithfulness for f in fields])
    overall_coverage = _mean_applicable([f.coverage for f in fields])
    overall_field_alignment = _mean_applicable([f.field_alignment for f in fields])
    overall_entity_attribution = _mean_applicable([f.entity_attribution for f in fields])
    overall_score = _mean_applicable([overall_faithfulness, overall_coverage, overall_field_alignment, overall_entity_attribution])
    statuses = {f.status for f in fields}
    if "INDETERMINATE" in statuses: status = "INDETERMINATE"
    elif "FAIL" in statuses: status = "FAIL"
    elif "WARN" in statuses: status = "WARN"
    elif statuses == {"NOT_APPLICABLE"}: status = "NOT_APPLICABLE"
    else: status = "PASS"
    return TranscriptMetrics(fields=fields, overall_faithfulness=overall_faithfulness, overall_coverage=overall_coverage, overall_field_alignment=overall_field_alignment, overall_entity_attribution=overall_entity_attribution, overall_score=overall_score, total_hallucinations=sum(f.hallucinations for f in fields), total_contradictions=sum(f.contradictions for f in fields), total_wrong_entity=sum(f.wrong_entity_count for f in fields), status=status)
