import pytest

from claims import NarrativeDecompositionError, claims_from_output_value, deterministic_claims
from models import OutputClaim


class FakeDecomposer:
    def decompose(self, field: str, value: str):
        return [
            OutputClaim(
                claim_id="ignored",
                claim="Fear of religious persecution",
                output_value=value,
            ),
            OutputClaim(
                claim_id="ignored2",
                claim="Threatened by former religious group",
                output_value=value,
            ),
        ]


class EmptyDecomposer:
    def decompose(self, field: str, value: str):
        return []


def test_list_values_are_deterministic_atomic_claims():
    claims = claims_from_output_value("medical_conditions", ["Diabetes", "Asthma"])
    assert [c.claim for c in claims] == ["Diabetes", "Asthma"]


def test_blank_list_items_are_removed_without_claim_id_gaps():
    claims = claims_from_output_value(
        "medical_conditions",
        ["Diabetes", "", "Asthma", "   "],
    )
    assert [c.claim for c in claims] == ["Diabetes", "Asthma"]
    assert [c.claim_id for c in claims] == [
        "medical_conditions:0",
        "medical_conditions:1",
    ]


def test_narrative_requires_semantic_decomposition():
    assert deterministic_claims("reason_for_claim", "A and B") is None
    with pytest.raises(ValueError):
        claims_from_output_value("reason_for_claim", "A and B")


def test_narrative_claim_ids_are_normalized_by_python():
    claims = claims_from_output_value(
        "reason_for_claim",
        "Fear of persecution and threats",
        decomposer=FakeDecomposer(),
    )
    assert [c.claim_id for c in claims] == [
        "reason_for_claim:0",
        "reason_for_claim:1",
    ]


def test_non_empty_narrative_with_zero_decomposed_claims_is_distinct_error():
    with pytest.raises(NarrativeDecompositionError, match="zero atomic claims"):
        claims_from_output_value(
            "reason_for_claim",
            "I fear persecution if I return.",
            decomposer=EmptyDecomposer(),
        )
