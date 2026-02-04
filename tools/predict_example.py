import argparse

from ml.smartcare_model.pipeline import (
    DEFAULT_MODEL_NAME,
    apply_overrides,
    build_feature_dataframe,
    load_artifacts,
    load_raw_dataframe,
    predict_from_features,
    prepare_prediction_row,
)


def main():
    parser = argparse.ArgumentParser(
        description="Predict admissions J+4 for a given date."
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date du jour J (format YYYY-MM-DD). Par defaut: derniere date disponible.",
    )
    parser.add_argument(
        "--meteo",
        type=str,
        default=None,
        help="Override meteo (ex: Pluie, Froid, Soleil, Canicule).",
    )
    parser.add_argument(
        "--event",
        type=str,
        default=None,
        help="Override evenement (ex: Epidemie_grippe, Canicule, Vague_froid, Aucun).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL_NAME,
        help="Nom du modele a utiliser (gradient_boosting ou random_forest).",
    )
    args = parser.parse_args()

    raw_df = load_raw_dataframe()
    feature_df = build_feature_dataframe(raw_df)
    model, feature_cols = load_artifacts(model_name=args.model)

    row = prepare_prediction_row(feature_df, feature_cols, target_date=args.date)
    row = apply_overrides(row, feature_cols, meteo=args.meteo, event=args.event)

    result = predict_from_features(row, model, feature_cols)
    print("date_J:", result["date_J"])
    print("prediction_J+4:", round(result["prediction"], 2))
    print("prediction_safe_J+4:", round(result["prediction_safe"], 2))


if __name__ == "__main__":
    main()
