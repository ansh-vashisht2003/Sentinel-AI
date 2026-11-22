"""
SENTINEL AI - SMS model trainer
Run from backend:
    python train_sms_model.py
Optional dataset override:
    python train_sms_model.py "../datasets/sms/sms_message_dataset_500.csv"
"""

import sys
from pathlib import Path

from sms import train_and_select_sms_model, DATASET_PATH

if __name__ == "__main__":
    dataset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATASET_PATH
    print("SENTINEL AI - SMS model training")
    print(f"Dataset: {dataset_path}")
    report = train_and_select_sms_model(dataset_path)
    print("\nTraining completed.")
    print(f"Selected model: {report['selected_model']}")
    print(f"Selection metric: {report['selection_metric']}")
    print(f"Dataset rows: {report['dataset_rows']}")
    print("\nModel ranking (CV macro-F1):")
    for row in report["model_comparison"]:
        print(
            f"- {row['model']}: CV macro-F1={row['cv_macro_f1_mean']:.4f} "
            f"(±{row['cv_macro_f1_std']:.4f}), holdout F1={row['holdout_macro_f1']:.4f}"
        )
    print(f"\nSaved model: {Path(__file__).resolve().parent / 'models' / 'sms_aiml_model.joblib'}")
    print(f"Saved comparison: {Path(__file__).resolve().parent / 'models' / 'sms_model_comparison.json'}")
