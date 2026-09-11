import pytest
from claims import claims_from_output_value, deterministic_claims
from models import OutputClaim

class FakeDecomposer:
    def decompose(self, field: str, value: str):
        return [OutputClaim(claim_id="ignored", claim="Fear of religious persecution", output_value=value), OutputClaim(claim_id="ignored2", claim="Threatened by former religious group", output_value=value)]

def test_list_values_are_deterministic_atomic_claims():
    claims = claims_from_output_value("medical_conditions", ["Diabetes", "Asthma"])
    assert [c.claim for c in claims] == ["Diabetes", "Asthma"]

def test_narrative_requires_semantic_decomposition():
    assert deterministic_claims("reason_for_claim", "A and B") is None
    with pytest.raises(ValueError): claims_from_output_value("reason_for_claim", "A and B")

def test_narrative_claim_ids_are_normalized_by_python():
    claims = claims_from_output_value("reason_for_claim", "Fear of persecution and threats", decomposer=FakeDecomposer())
    assert [c.claim_id for c in claims] == ["reason_for_claim:0", "reason_for_claim:1"]
