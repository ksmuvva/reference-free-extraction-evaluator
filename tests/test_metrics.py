from metrics import calculate_field_metrics, calculate_transcript_metrics
from models import ClaimDecision, EvaluationEvidence, SourceFactDecision

def decision(claim_id: str, *, supported=True, correct_field=True, entity_correct=True, contradiction=False):
    return ClaimDecision(claim_id=claim_id, claim=claim_id, supported=supported, correct_field=correct_field, entity_correct=entity_correct, contradiction=contradiction, matched_source_fact_ids=["f:source:0"] if supported else [])

def test_no_claims_no_facts_is_not_applicable_not_perfect():
    m = calculate_field_metrics(EvaluationEvidence(field="f", output_value=""))
    assert m.faithfulness is None and m.coverage is None and m.status == "NOT_APPLICABLE"

def test_empty_output_with_source_facts_fails_with_zero_coverage():
    m = calculate_field_metrics(EvaluationEvidence(field="f", output_value="", source_facts=[SourceFactDecision(fact_id="f:source:0", fact="Diabetes", captured=False)]))
    assert m.coverage == 0.0 and m.status == "FAIL"

def test_critical_defect_is_hard_fail_without_fake_threshold_logic():
    m = calculate_field_metrics(EvaluationEvidence(field="f", output_value=["A","B"], output_claims=[decision("f:0"), decision("f:1", supported=False)], source_facts=[SourceFactDecision(fact_id="f:source:0", fact="A", captured=True)]))
    assert m.faithfulness == 0.5 and m.hallucinations == 1 and m.status == "FAIL"

def test_transcript_ignores_not_applicable_values_in_averages():
    applicable = calculate_field_metrics(EvaluationEvidence(field="a", output_value=["A"], output_claims=[decision("a:0")], source_facts=[SourceFactDecision(fact_id="f:source:0", fact="A", captured=True)]))
    na = calculate_field_metrics(EvaluationEvidence(field="b", output_value=""))
    t = calculate_transcript_metrics([applicable, na])
    assert t.overall_faithfulness == 1.0 and t.status == "PASS"
