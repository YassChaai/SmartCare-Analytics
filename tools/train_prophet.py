from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ml"))

from tools.train_poc import run


if __name__ == "__main__":
    run(["--prophet-only"] + sys.argv[1:])
