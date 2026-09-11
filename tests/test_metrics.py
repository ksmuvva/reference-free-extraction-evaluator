from claims import claims_from_output_value
from metrics import calculate_field_metrics, calculate_transcript_metrics
from models import ClaimDecision, EvaluationEvidence, FieldMetrics, SourceFactDecision


def test_output_values_become_claim_json_first():
    claims = claims_from_output_value("medical_conditions", ["Diabetes", "Asthma"])
    assert [c.claim for c in claims] == ["Diabetes", "Asthma"]


def test_metrics_are_derived_from_boolean_evidence():
    evidence = EvaluationEvidence(
        field="medical_conditions",
        output_value=["Diabetes", "Hypertension"],
        output_claims=[
            ClaimDecision(
                claim_id="medical_conditions:0",
                claim="Diabetes",
                supported=True,
                correct_field=True,
                entity_correct=True,
                contradiction=False,
                evidence_questions=[22],
            ),
            ClaimDecision(
                claim_id="medical_conditions:1",
                claim="Hypertension",
                supported=False,
                correct_field=True,
                entity_correct=True,
                contradiction=False,
                evidence_questions=[],
            ),
        ],
        source_facts=[
            SourceFactDecision(
                fact_id="medical_conditions:source:0",
                fact="Diabetes",
                captured=True,
                evidence_questions=[22],
            ),
            SourceFactDecision(
                fact_id="medical_conditions:source:1",
                fact="Asthma",
                captured=False,
                evidence_questions=[37],
            ),
        ],
        issues=["Hypertension unsupported; asthma omitted."],
    )

    result = calculate_field_metrics(evidence)

    assert result.faithfulness == 0.5
    assert result.coverage == 0.5
    assert result.field_alignment == 1.0
    assert result.entity_attribution == 1.0
    assert result.hallucinations == 1
    assert result.status == "FAIL"


def test_transcript_metrics_are_deterministic():
    fields = [
        FieldMetrics(
            field="reason_for_claim",
            faithfulness=1.0,
            coverage=1.0,
            field_alignment=1.0,
            entity_attribution=1.0,
            hallucinations=0,
            contradictions=0,
            status="PASS",
        ),
        FieldMetrics(
            field="medical_conditions",
            faithfulness=1.0,
            coverage=0.8,
            field_alignment=1.0,
            entity_attribution=1.0,
            hallucinations=0,
            contradictions=0,
            status="WARN",
        ),
    ]

    result = calculate_transcript_metrics(fields)
    assert result.overall_coverage == 0.9
    assert result.overall_score == 0.975
    assert result.status == "WARN"
