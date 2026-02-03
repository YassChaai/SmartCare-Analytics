from smartcare_model.pipeline import train_models


def main():
    results = train_models()
    print("=== Evaluation (test) ===")
    for name, metrics in results.items():
        print(f"{name}: {metrics}")


if __name__ == "__main__":
    main()
