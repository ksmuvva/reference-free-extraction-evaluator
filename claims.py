from typing import Any
from models import OutputClaim


def claims_from_output_value(field: str, value: Any) -> list[OutputClaim]:
    """
    Deterministically convert the EXISTING output value into auditable claim objects.

    No inference.
    No correction.
    No replacement extraction.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [
            OutputClaim(
                claim_id=f"{field}:{i}",
                claim=str(item),
                output_value=item,
            )
            for i, item in enumerate(value)
        ]

    if isinstance(value, dict):
        return [
            OutputClaim(
                claim_id=f"{field}:{key}",
                claim=f"{key}: {item}",
                output_value={key: item},
            )
            for key, item in value.items()
        ]

    return [
        OutputClaim(
            claim_id=f"{field}:0",
            claim=str(value),
            output_value=value,
        )
    ]
