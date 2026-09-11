import pytest
from models import ClaimDecision, OutputClaim, SourceFact, SourceFactDecision
from validation import JudgeContractError, validate_claim_decisions, validate_output_schema, validate_source_fact_decisions

def test_schema_validation_is_mandatory():
    result = validate_output_schema({"medical_conditions": ["Diabetes"]})
    assert result.schema_valid is False and "reason_for_claim" in result.missing_fields

def test_missing_claim_decision_is_rejected():
    expected = [OutputClaim(claim_id="f:0", claim="A", output_value="A"), OutputClaim(claim_id="f:1", claim="B", output_value="B")]
    returned = [ClaimDecision(claim_id="f:0", claim="A", supported=True, correct_field=True, entity_correct=True, contradiction=False, matched_source_fact_ids=["f:source:0"])]
    with pytest.raises(JudgeContractError): validate_claim_decisions(expected, returned)

def test_fact_text_mutation_is_rejected():
    expected = [SourceFact(fact_id="f:source:0", fact="Diabetes")]
    returned = [SourceFactDecision(fact_id="f:source:0", fact="Hypertension", captured=True)]
    with pytest.raises(JudgeContractError): validate_source_fact_decisions(expected, returned)
