# Predictive Maintenance Failure Prediction for Industrial Equipment Using Machine Learning

Capstone project for AAI201 Machine Learning at DMACC. Predicts machine failures from sensor and process data on the AI4I 2020 dataset using a baseline-to-ensemble model progression, with class imbalance handling, threshold tuning, and a fairness check across product quality types.

## Problem

Unplanned downtime in manufacturing is expensive. A model that flags machines likely to fail in the near term lets maintenance teams intervene before failure, reducing downtime and scrap. The cost of a missed failure (false negative) is much higher than the cost of an unnecessary inspection (false positive), so the evaluation prioritizes recall and threshold tuning rather than raw accuracy.

## Dataset

AI4I 2020 Predictive Maintenance Dataset from the UCI Machine Learning Repository. 10,000 synthetic samples, 14 columns, ~3.4% positive class (failure). Synthetic origin is a known limitation and is discussed in the reflection.

Source: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

The notebook fetches the data automatically via `ucimlrepo` (with a direct CSV fallback). No manual download is required.

## Approach

- Baseline models: Logistic Regression (L2), Decision Tree (depth-limited)
- Ensembles: Random Forest, HistGradientBoostingClassifier with validation-based early stopping
- Class imbalance: `class_weight='balanced'` plus probability-threshold tuning on the validation set
- Overfitting prevention: regularization, early stopping, and 5-fold stratified cross-validation
- Fairness: per-`Type` (L/M/H quality) recall and precision check on the validation set
- Final evaluation on a held-out test set with the tuned threshold

## Repository structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
├── predictive_maintenance.ipynb
├── reflection.md
└── presentation/
    └── AAI201 Capstone Drew Menning.pptx
```

## Setup

```bash
git clone <this-repo>
cd ai4i-predictive-maintenance
python -m venv .venv
. .venv/Scripts/activate    # on Windows; use source .venv/bin/activate on Mac/Linux
pip install -r requirements.txt
jupyter notebook predictive_maintenance.ipynb
```

Run all cells top to bottom. Total runtime is under two minutes on a laptop.

## Results

The held-out test-set numbers are produced by the notebook on each run. Headline metrics for the final HistGradientBoosting model with the tuned threshold are reported in the notebook's final evaluation cell and in the presentation.

## Ethical considerations

The AI4I 2020 dataset is synthetic and does not contain personal data, so privacy risk is low. Two issues that do apply: class imbalance can bias the model toward predicting non-failure, addressed here with `class_weight='balanced'` plus threshold tuning rather than synthetic oversampling on top of synthetic data; and fairness across product quality types (L, M, H), which the notebook checks by reporting per-type recall and precision on the validation set. Synthetic origin is itself a limitation: any deployment claim has to be tested on real industrial data, with a threshold tied to actual maintenance costs rather than F1.

## Presentation

Slides and speaker notes are in `presentation/`. A recorded walkthrough is linked in Canvas.

## Author

Drew Menning, DMACC AAS in AI, AAI201 Spring 2026.
