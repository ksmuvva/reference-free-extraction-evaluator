# Reference-Free Structured Extraction Evaluation — v3

## Purpose
Validate an existing structured extraction against the entire source asylum-interview Q&A JSON. The evaluator is read-only and never repairs, rewrites, or regenerates production output.

## Core design
```text
Production output JSON
        |
        +--> mandatory schema/type validation (Python)
        |
        +--> deterministic Python field loop
                |
                +--> output claim creation
                |      - list/dict: deterministic
                |      - narrative text: semantic atomic decomposition
                |
                +--> independent source-fact inventory
                |      - entire source interview
                |      - field semantics only
                |      - production output is NOT shown to this pass
                |
                +--> evidence verification
                |      - fixed claims + fixed source facts
                |
                +--> strict judge-contract reconciliation (Python)
                |
                +--> deterministic metrics and status
```

## v3 changes
1. **No LLM-controlled orchestration.** Python owns field iteration and sequencing.
2. **Independent source-fact inventory.** Coverage denominator is created in a separate pass that does not see production output.
3. **Atomic narrative claims.** Narrative strings are decomposed before scoring; Python normalizes claim IDs.
4. **Judge reconciliation.** Missing, extra, duplicate, or rewritten claim/fact IDs/text yield `INDETERMINATE`.
5. **Explicit zero-denominator semantics.** No denominator silently becomes `1.0`.

## Metrics
- faithfulness = supported output claims / output claims
- coverage = captured source facts / fixed source-fact inventory
- field alignment = correctly placed claims / output claims
- entity attribution = correctly attributed claims / output claims
- hallucination, contradiction, and wrong-entity counts are also reported

## Status policy
Unsupported claims, contradictions, and wrong-person/entity attribution are hard failures. Coverage and field alignment are graded through environment thresholds. Faithfulness thresholds are intentionally not used after a zero-tolerance hallucination rule, eliminating unreachable scoring branches.

## Empty / uncertain cases
- no claims + no source facts -> `NOT_APPLICABLE`
- no claims + relevant source facts -> coverage `0.0`, `FAIL`
- invalid judge contract -> `INDETERMINATE`

## Schema validation
Missing required fields or wrong types fail before semantic evaluation. Unexpected fields are reported and can downgrade an otherwise passing transcript to `WARN`.

## Configuration
`OPENAI_API_KEY` is a local secret only. Model/threshold settings are centralized in `config.py` and mirrored in `.env.example`.

## Testing
Offline CI covers schema gating, atomic claim behavior, judge-contract validation, empty-field semantics, hard-failure logic, deterministic orchestration using a fake judge, and `INDETERMINATE` behavior. Live semantic tests are separate because they require an API key.

## Limits
There is no human-labelled gold output. Do not claim formal accuracy, precision, recall, F1, ROUGE, BLEU, or exact match. Arithmetic is deterministic; semantic evidence remains model-assisted.
