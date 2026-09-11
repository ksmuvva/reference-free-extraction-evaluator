import json
import sys
from pathlib import Path
from judge import DspySemanticJudge
from pipeline import evaluate_transcript

def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        print("Usage: python main.py source.json actual_output.json", file=sys.stderr)
        return 2
    report = evaluate_transcript(load_json(argv[0]), load_json(argv[1]), DspySemanticJudge())
    print(report.model_dump_json(indent=2))
    return 0 if report.metrics.status in {"PASS", "WARN", "NOT_APPLICABLE"} else 1

if __name__ == "__main__":
    raise SystemExit(main())
