# Reference-Free Extraction Evaluator v3

Validation-only framework for comparing an existing structured extraction JSON with the entire source asylum-interview Q&A JSON. It does **not** repair or regenerate production output.

## Architecture

The critical path is deliberately **not agent-orchestrated**. Python owns schema validation, the field loop, contract checks, arithmetic, thresholds, and aggregation. The LLM is limited to semantic work that Python cannot do reliably by rules alone.

```text
Actual production output JSON
        |
        +--> mandatory schema/type validation (Python)
        |
        +--> for each field (Python loop)
                |
                +--> atomic output claims
                |      - list/dict: deterministic
                |      - narrative text: semantic decomposition
                |
                +--> source-fact inventory
                |      - independent semantic pass over entire source
                |      - does NOT see production output
                |
                +--> evidence verification
                |      - fixed claims + fixed source facts
                |      - supported/captured/aligned/entity/contradiction
                |
                +--> strict contract reconciliation (Python)
                |
                +--> deterministic metrics (Python)
```

This separates **source-fact discovery** from **output verification**, reducing correlated judge error in coverage measurement.

## Metrics

- Faithfulness = supported output claims / output claims
- Coverage = captured source facts / fixed source-fact inventory
- Field alignment = correctly placed claims / output claims
- Entity attribution = correctly attributed claims / output claims
- Hallucination count = unsupported claims
- Contradiction count
- Wrong-entity count

The arithmetic is deterministic; semantic classifications are LLM-assisted.

### Status policy

Critical defects are hard failures:
- unsupported claim / hallucination
- contradiction
- wrong-person/entity attribution

Coverage and field alignment are graded using policy thresholds from environment variables. Faithfulness thresholds are intentionally **not** used after a hard hallucination rule, avoiding unreachable/dead scoring logic.

`NOT_APPLICABLE` and `INDETERMINATE` are explicit states. A zero denominator never silently becomes `1.0`.

## Judge safety checks

Python rejects judge responses that:
- omit or add claims
- duplicate claim/fact IDs
- alter claim/fact text
- omit or add source facts
- reference unknown source-fact IDs
- mark a claim supported without linking it to at least one fixed source fact

A contract failure becomes `INDETERMINATE`, not a misleading score.

## Configuration

Copy `.env.example` locally or export variables in your shell. Never commit real API keys.

```bash
export OPENAI_API_KEY="..."
export JUDGE_MODEL="openai/gpt-5.6"
```

The exposed key previously pasted into chat should be revoked and must not be reused.

## Run deterministic tests without an API key

```bash
python -m pip install -r requirements.lock
pytest -q
```

## Run a live evaluation later

```bash
python -m pip install -e '.[test]'
python main.py data/source.json data/actual_output.json
```

A live run requires `OPENAI_API_KEY` and the configured judge model.

## Interpretation limits

There is no human-labelled gold output, so this project does not claim formal accuracy, precision, recall, F1, ROUGE, BLEU, or exact-match accuracy. Coverage remains a judge-assisted semantic completeness measure even though its arithmetic is deterministic.
