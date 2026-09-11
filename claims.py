from typing import Any, Protocol
from models import OutputClaim

class NarrativeClaimDecomposer(Protocol):
    def decompose(self, field: str, value: str) -> list[OutputClaim]: ...

def deterministic_claims(field: str, value: Any) -> list[OutputClaim] | None:
    if value is None:
        return []
    if isinstance(value, list):
        return [OutputClaim(claim_id=f"{field}:{i}", claim=str(item), output_value=item) for i, item in enumerate(value) if str(item).strip()]
    if isinstance(value, dict):
        return [OutputClaim(claim_id=f"{field}:{key}", claim=f"{key}: {item}", output_value={key: item}) for key, item in value.items()]
    if isinstance(value, str):
        return [] if not value.strip() else None
    return [OutputClaim(claim_id=f"{field}:0", claim=str(value), output_value=value)]

def claims_from_output_value(field: str, value: Any, decomposer: NarrativeClaimDecomposer | None = None) -> list[OutputClaim]:
    claims = deterministic_claims(field, value)
    if claims is not None:
        return claims
    if decomposer is None:
        raise ValueError(f"Narrative field {field!r} requires an atomic claim decomposer.")
    decomposed = decomposer.decompose(field, value)
    return [OutputClaim(claim_id=f"{field}:{i}", claim=claim.claim.strip(), output_value=value) for i, claim in enumerate(decomposed) if claim.claim.strip()]
