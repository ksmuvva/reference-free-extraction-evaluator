import json

from agents import Agent, Runner, function_tool

from claims import claims_from_output_value
from config import OUTPUT_SCHEMA
from judge import build_evaluation_evidence
from metrics import calculate_field_metrics, calculate_transcript_metrics
from models import EvaluationEvidence, FieldMetrics, OutputClaim


@function_tool
def inspect_schema(actual_output_json: str) -> str:
    """Deterministically inspect the existing structured output."""
    try:
        data = json.loads(actual_output_json)
    except json.JSONDecodeError as exc:
        return json.dumps({"json_valid": False, "error": str(exc)})

    missing = [f for f in OUTPUT_SCHEMA if f not in data]
    wrong_types = [
        f for f, expected in OUTPUT_SCHEMA.items()
        if f in data and not isinstance(data[f], expected)
    ]

    return json.dumps({
        "json_valid": True,
        "schema_valid": not missing and not wrong_types,
        "missing_fields": missing,
        "wrong_type_fields": wrong_types,
        "fields": list(data.keys()),
    })


@function_tool
def create_output_claims(field_name: str, actual_field_value_json: str) -> str:
    """Build claim JSON from the ACTUAL output field value before semantic checking."""
    value = json.loads(actual_field_value_json)
    claims = claims_from_output_value(field_name, value)
    return json.dumps([c.model_dump(mode="json") for c in claims])


@function_tool
def create_evaluation_evidence(
    source_json: str,
    field_name: str,
    actual_field_value_json: str,
    output_claims_json: str,
) -> str:
    """Compare supplied output claims against the ENTIRE input JSON."""
    source = json.loads(source_json)
    value = json.loads(actual_field_value_json)
    claims = [OutputClaim.model_validate(x) for x in json.loads(output_claims_json)]

    evidence = build_evaluation_evidence(
        source=source,
        field_name=field_name,
        value=value,
        claims=claims,
    )
    return evidence.model_dump_json()


@function_tool
def calculate_field_score(evaluation_evidence_json: str) -> str:
    """Deterministically calculate field metrics from evidence JSON."""
    evidence = EvaluationEvidence.model_validate_json(evaluation_evidence_json)
    return calculate_field_metrics(evidence).model_dump_json()


@function_tool
def calculate_overall_metrics(field_metrics_json: str) -> str:
    """Deterministically aggregate field metrics for the whole transcript."""
    items = json.loads(field_metrics_json)
    fields = [FieldMetrics.model_validate(x) for x in items]
    return calculate_transcript_metrics(fields).model_dump_json()


evaluation_agent = Agent(
    name="Structured Extraction Validation Agent",
    model="gpt-5.6",
    instructions="""
You are a READ-ONLY evaluation agent.

You receive:
1. original asylum interview Q&A JSON
2. actual structured output JSON produced by the system under test

Never modify, correct, repair, or regenerate the output.

For every field:
1. call create_output_claims on the ACTUAL field value
2. call create_evaluation_evidence using those exact claims and the ENTIRE source interview
3. call calculate_field_score on the resulting evidence JSON

After all fields:
4. call calculate_overall_metrics once
5. return the evidence JSON plus final metrics

The LLM judge makes only boolean/categorical semantic decisions.
Python calculates all ratios, counts, thresholds, and overall metrics.
""",
    tools=[
        inspect_schema,
        create_output_claims,
        create_evaluation_evidence,
        calculate_field_score,
        calculate_overall_metrics,
    ],
)


def evaluate_transcript(source: dict, actual_output: dict) -> str:
    prompt = f"""
ORIGINAL SOURCE JSON:
{json.dumps(source, ensure_ascii=False)}

ACTUAL STRUCTURED OUTPUT JSON:
{json.dumps(actual_output, ensure_ascii=False)}

Evaluate only.
"""
    return str(Runner.run_sync(evaluation_agent, prompt).final_output)
