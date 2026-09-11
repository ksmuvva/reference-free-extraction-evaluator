from statistics import mean

from models import EvaluationEvidence, FieldMetrics, TranscriptMetrics


def ratio(numerator: int, denominator: int) -> float:
    return 1.0 if denominator == 0 else round(numerator / denominator, 4)


def calculate_field_metrics(evidence: EvaluationEvidence) -> FieldMetrics:
    claims = evidence.output_claims
    facts = evidence.source_facts

    faithfulness = ratio(sum(1 for c in claims if c.supported), len(claims))
    coverage = ratio(sum(1 for f in facts if f.captured), len(facts))
    field_alignment = ratio(sum(1 for c in claims if c.correct_field), len(claims))
    entity_attribution = ratio(sum(1 for c in claims if c.entity_correct), len(claims))

    hallucinations = sum(1 for c in claims if not c.supported)
    contradictions = sum(1 for c in claims if c.contradiction)

    if hallucinations or contradictions or entity_attribution < 1.0:
        status = "FAIL"
    elif faithfulness >= 0.95 and coverage >= 0.90 and field_alignment >= 0.95:
        status = "PASS"
    elif faithfulness >= 0.80 and coverage >= 0.75:
        status = "WARN"
    else:
        status = "FAIL"

    return FieldMetrics(
        field=evidence.field,
        faithfulness=faithfulness,
        coverage=coverage,
        field_alignment=field_alignment,
        entity_attribution=entity_attribution,
        hallucinations=hallucinations,
        contradictions=contradictions,
        status=status,
        issues=evidence.issues,
    )


def calculate_transcript_metrics(fields: list[FieldMetrics]) -> TranscriptMetrics:
    if not fields:
        return TranscriptMetrics(
            fields=[],
            overall_faithfulness=0.0,
            overall_coverage=0.0,
            overall_field_alignment=0.0,
            overall_entity_attribution=0.0,
            overall_score=0.0,
            total_hallucinations=0,
            total_contradictions=0,
            status="FAIL",
        )

    overall_faithfulness = round(mean(f.faithfulness for f in fields), 4)
    overall_coverage = round(mean(f.coverage for f in fields), 4)
    overall_field_alignment = round(mean(f.field_alignment for f in fields), 4)
    overall_entity_attribution = round(mean(f.entity_attribution for f in fields), 4)

    overall_score = round(mean([
        overall_faithfulness,
        overall_coverage,
        overall_field_alignment,
        overall_entity_attribution,
    ]), 4)

    total_hallucinations = sum(f.hallucinations for f in fields)
    total_contradictions = sum(f.contradictions for f in fields)

    if total_hallucinations or total_contradictions or overall_entity_attribution < 1.0 or any(f.status == "FAIL" for f in fields):
        status = "FAIL"
    elif any(f.status == "WARN" for f in fields):
        status = "WARN"
    else:
        status = "PASS"

    return TranscriptMetrics(
        fields=fields,
        overall_faithfulness=overall_faithfulness,
        overall_coverage=overall_coverage,
        overall_field_alignment=overall_field_alignment,
        overall_entity_attribution=overall_entity_attribution,
        overall_score=overall_score,
        total_hallucinations=total_hallucinations,
        total_contradictions=total_contradictions,
        status=status,
    )
