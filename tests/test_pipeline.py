from models import ClaimDecision, EvaluationEvidence, OutputClaim, SourceFact, SourceFactDecision
from pipeline import evaluate_transcript

class FakeJudge:
    def decompose(self, field: str, value: str):
        return [OutputClaim(claim_id="x", claim=value, output_value=value)]
    def inventory_source_facts(self, source: dict, field: str):
        return [SourceFact(fact_id=f"{field}:source:0", fact="Supported fact", evidence_questions=[1])]
    def verify(self, source, field, value, claims, source_facts):
        return EvaluationEvidence(field=field, output_value=value, output_claims=[ClaimDecision(claim_id=c.claim_id, claim=c.claim, supported=True, correct_field=True, entity_correct=True, contradiction=False, matched_source_fact_ids=[source_facts[0].fact_id], evidence_questions=[1]) for c in claims], source_facts=[SourceFactDecision(fact_id=source_facts[0].fact_id, fact=source_facts[0].fact, captured=True, evidence_questions=[1])])

class BrokenJudge(FakeJudge):
    def verify(self, source, field, value, claims, source_facts):
        evidence = super().verify(source, field, value, claims, source_facts)
        evidence.output_claims = []
        return evidence

VALID_OUTPUT = {"reason_for_claim":"Supported fact","medical_conditions":["Supported fact"],"family_relationships":"Supported fact","countries_travelled":["Supported fact"]}

def test_python_owns_field_loop_and_schema_gate():
    report = evaluate_transcript({"interview": []}, VALID_OUTPUT, FakeJudge())
    assert len(report.evidence) == 4 and report.metrics.status == "PASS"

def test_judge_contract_failure_becomes_indeterminate():
    report = evaluate_transcript({"interview": []}, VALID_OUTPUT, BrokenJudge())
    assert report.metrics.status == "INDETERMINATE"
    assert any("contract violation" in issue.lower() for issue in report.evidence[0].issues)
