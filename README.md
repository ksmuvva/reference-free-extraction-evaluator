# Reference-Free Extraction Evaluator

Evaluation-only agent for validating an existing structured JSON extraction against the entire source asylum interview Q&A JSON.

## Three-layer design

### Layer 1 - Actual production output JSON
The evaluator starts with the exact structured output produced by the system under test.

### Layer 2 - Evaluation evidence JSON
Each output field value is first converted into explicit claim objects. DSPy + the LLM judge checks those exact claims against the ENTIRE input Q&A JSON and returns boolean/categorical decisions such as `supported`, `correct_field`, `entity_correct`, `contradiction`, and source evidence question numbers.

The judge also identifies material source facts relevant to each field and marks each one `captured=true/false`.

### Layer 3 - Deterministic metrics
Python computes:

- faithfulness = supported output claims / total output claims
- coverage = captured relevant source facts / total relevant source facts
- field alignment = correctly placed claims / total output claims
- entity attribution = correctly attributed claims / total output claims
- hallucination count
- contradiction count

The LLM never directly produces decimal quality scores.

## Stack

- OpenAI Agents SDK: tool-using evaluation agent
- DSPy + LLM-as-judge: semantic boolean/categorical decisions
- Python: claim normalisation, arithmetic, thresholds and aggregation

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
export OPENAI_API_KEY=...
export JUDGE_MODEL=openai/gpt-5.6
pytest -q
python main.py data/source.json data/actual_output.json
```

No gold/reference output is required. Therefore the project does not claim formal accuracy, precision, recall, F1, ROUGE, BLEU, or exact match.
