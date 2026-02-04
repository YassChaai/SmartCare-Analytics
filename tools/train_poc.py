from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ml"))

from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ml"))

from smartcare_model.pipeline import train_models, train_prophet_model


def run(argv=None):
    parser = argparse.ArgumentParser(description="Train SmartCare models (classics + Prophet)")
    parser.add_argument("--classic-only", action="store_true", help="Train only classic models")
    parser.add_argument("--prophet-only", action="store_true", help="Train only Prophet")
    parser.add_argument("--tune", action="store_true", help="Grid tune Prophet hyperparameters")
    args = parser.parse_args(argv)

    run_classic = not args.prophet_only
    run_prophet = not args.classic_only

    results = {}
    if run_classic:
        results.update(train_models())
    if run_prophet:
        results.update(train_prophet_model(tune=args.tune))

    print("=== Evaluation (test) ===")
    for name, metrics in results.items():
        print(f"{name}: {metrics}")


if __name__ == "__main__":
    run()
