from claims import claims_from_output_value
from judge import SemanticJudge
from metrics import calculate_field_metrics, calculate_transcript_metrics
from models import EvaluationEvidence, EvaluationReport, FieldMetrics
from validation import JudgeContractError, validate_claim_decisions, validate_cross_references, validate_output_schema, validate_source_fact_decisions

def evaluate_transcript(source: dict, actual_output: dict, judge: SemanticJudge) -> EvaluationReport:
    schema = validate_output_schema(actual_output)
    if not schema.schema_valid:
        metrics = calculate_transcript_metrics([])
        metrics.status = "FAIL"
        return EvaluationReport(schema_result=schema, evidence=[], metrics=metrics)
    evidence_items, field_metrics = [], []
    for field, value in actual_output.items():
        if field in schema.unexpected_fields:
            continue
        try:
            claims = claims_from_output_value(field, value, decomposer=judge)
            source_facts = judge.inventory_source_facts(source, field)
            evidence = judge.verify(source, field, value, claims, source_facts)
            validate_claim_decisions(claims, evidence.output_claims)
            validate_source_fact_decisions(source_facts, evidence.source_facts)
            validate_cross_references(evidence.output_claims, source_facts)
            metrics = calculate_field_metrics(evidence)
        except JudgeContractError as exc:
            evidence = EvaluationEvidence(field=field, output_value=value, issues=[f"Judge contract violation: {exc}"])
            metrics = FieldMetrics(field=field, faithfulness=None, coverage=None, field_alignment=None, entity_attribution=None, hallucinations=0, contradictions=0, wrong_entity_count=0, status="INDETERMINATE", issues=evidence.issues)
        evidence_items.append(evidence)
        field_metrics.append(metrics)
    transcript = calculate_transcript_metrics(field_metrics)
    if schema.unexpected_fields and transcript.status == "PASS":
        transcript.status = "WARN"
    return EvaluationReport(schema_result=schema, evidence=evidence_items, metrics=transcript)
