import json
import os
import dspy

from config import FIELD_DEFINITIONS
from models import EvaluationEvidence, OutputClaim


MODEL_NAME = os.getenv("JUDGE_MODEL", "openai/gpt-5.6")
dspy.configure(lm=dspy.LM(MODEL_NAME))


class FieldEvidenceJudge(dspy.Signature):
    """
    Produce EVALUATION EVIDENCE for one existing output field.

    Inputs:
    - entire source interview JSON
    - destination field name and definition
    - actual output field value
    - claim objects created from that exact output value

    Evaluation only:
    - do not correct the field
    - do not regenerate extraction
    - do not create replacement output
    - do not assign decimal quality scores

    For every supplied output claim decide:
      supported: true/false
      correct_field: true/false
      entity_correct: true/false
      contradiction: true/false
      evidence_questions: source question numbers

    Then inspect the ENTIRE source interview and identify material source facts
    relevant to this field. For every source fact decide:
      captured: true/false
      evidence_questions: source question numbers

    Relevant evidence may appear under any question number.
    """

    source_json: str = dspy.InputField()
    field_name: str = dspy.InputField()
    field_definition: str = dspy.InputField()
    actual_field_value_json: str = dspy.InputField()
    output_claims_json: str = dspy.InputField()

    evidence: EvaluationEvidence = dspy.OutputField()


judge = dspy.Predict(FieldEvidenceJudge)


def build_evaluation_evidence(
    source: dict,
    field_name: str,
    value,
    claims: list[OutputClaim],
) -> EvaluationEvidence:
    response = judge(
        source_json=json.dumps(source, ensure_ascii=False),
        field_name=field_name,
        field_definition=FIELD_DEFINITIONS.get(field_name, field_name),
        actual_field_value_json=json.dumps(value, ensure_ascii=False),
        output_claims_json=json.dumps(
            [c.model_dump(mode="json") for c in claims],
            ensure_ascii=False,
        ),
    )
    return response.evidence
