import json
import sys
from pathlib import Path

from agent import evaluate_transcript


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python main.py source.json actual_output.json")

    print(evaluate_transcript(load(sys.argv[1]), load(sys.argv[2])))
