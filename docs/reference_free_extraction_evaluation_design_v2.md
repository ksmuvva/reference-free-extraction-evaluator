# Reference-Free Structured Extraction Evaluation Design

## Purpose

Validate an existing structured extraction result against the original asylum interview Q&A JSON before PDF generation. The evaluator is read-only: it must not correct, rewrite, repair, or regenerate the production output.

## Three-layer design

### 1. Actual production output JSON

Use the exact structured JSON produced by the system under test.

### 2. Evaluation evidence JSON

For each output field:

1. Convert the existing output value into explicit claim objects.
2. Compare each claim with the entire source interview JSON.
3. Return boolean/categorical semantic decisions only:
   - `supported`
   - `correct_field`
   - `entity_correct`
   - `contradiction`
   - `evidence_questions`
4. Independently identify material source facts relevant to the field and mark each `captured=true/false`.

Evidence may occur under any interview question number.

Example:

```json
{
  "field": "medical_conditions",
  "output_claims": [
    {
      "claim": "Diabetes",
      "supported": true,
      "correct_field": true,
      "entity_correct": true,
      "contradiction": false,
      "evidence_questions": [22]
    }
  ],
  "source_facts": [
    {
      "fact": "Asthma",
      "captured": false,
      "evidence_questions": [37]
    }
  ]
}
```

### 3. Deterministic Python metrics

The LLM does not directly generate decimal scores. Python calculates:

```text
faithfulness = supported output claims / total output claims
coverage = captured relevant source facts / total relevant source facts
field alignment = correctly placed claims / total output claims
entity attribution = correctly attributed claims / total output claims
hallucination count = unsupported output claims
contradiction count = contradictory output claims
```

## Status logic

Critical semantic defects override average quality scores:

```python
if hallucinations > 0:
    status = "FAIL"
elif contradictions > 0:
    status = "FAIL"
elif entity_attribution < 1.0:
    status = "FAIL"
elif faithfulness >= 0.95 and coverage >= 0.90 and field_alignment >= 0.95:
    status = "PASS"
elif faithfulness >= 0.80 and coverage >= 0.75:
    status = "WARN"
else:
    status = "FAIL"
```

## Architecture

```text
OpenAI Agents SDK evaluation agent
        |
        +-- inspect_schema()
        |
        +-- create_output_claims()
        |       deterministic
        |
        +-- create_evaluation_evidence()
        |       DSPy + LLM-as-judge
        |       boolean/categorical decisions only
        |
        +-- calculate_field_score()
        |       deterministic Python
        |
        +-- calculate_overall_metrics()
                deterministic Python
```

## Deterministic versus LLM-assisted responsibilities

### Deterministic

- JSON validity
- schema validity
- required-field presence
- type checks
- claim normalisation from simple output values
- counts and ratios
- thresholds
- field status
- transcript aggregation

### LLM-assisted semantic judgement

- whether an output claim is semantically supported
- locating supporting source questions
- whether a claim belongs in the correct target field
- whether information belongs to the applicant or another entity
- contradiction detection
- identification of material source facts and whether they were captured

## Important limitation

The arithmetic is deterministic, but the underlying semantic classifications are still LLM judgements. This is more auditable than direct LLM scoring but is not equivalent to a human-labelled gold dataset.

Because no gold/reference structured output exists, do not report formal accuracy, precision, recall, F1, ROUGE, BLEU, or exact-match accuracy.
