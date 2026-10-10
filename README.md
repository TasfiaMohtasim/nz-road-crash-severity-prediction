# New Zealand Road Crash Severity Prediction

This project investigates whether machine-learning models can classify the severity of already recorded New Zealand road crashes using Crash Analysis System (CAS) attributes together with spatial, socioeconomic, land-cover, and terrain context.

The target variable is crash severity with four classes:

- Non-Injury Crash
- Minor Crash
- Serious Crash
- Fatal Crash

The project does **not** predict whether a crash will occur or the probability of a future crash.

## Final Model

The final national-context model uses:

- 30 CAS baseline predictors
- Distance to the nearest road-network junction
- NZDep2023 socioeconomic deprivation score
- LCDB land-cover group
- LINZ elevation

Total predictors: **34**

The final five-seed comparison produced:

| Metric | CAS Only | Final National Context |
|---|---:|---:|
| Accuracy | 0.4940 | 0.5184 |
| Balanced Accuracy | 0.4062 | 0.3947 |
| Macro F1 | 0.3288 | 0.3389 |
| Fatal Recall | 0.3077 | 0.2215 |
| Serious Recall | 0.3944 | 0.3756 |

Macro F1 improved in all five evaluated random seeds, with a mean paired gain of **+0.0101**. The improvement in overall Accuracy and Macro F1 came with lower severe-class recall, which remains an important limitation of the model.

## Project Structure

```text
Project_Roadcrash/
├── app.py
├── README.md
├── requirements.txt
├── Notebook/
│   ├── 01_Notebook1.ipynb
│   ├── 02_Spatial_Feature_Experiment.ipynb
│   ├── 03_results_summary.ipynb
│   ├── 04_nzdep_experiment.ipynb
│   ├── 05_gch23_experiment.ipynb
│   ├── 06_landcover_experiment.ipynb
│   ├── 07_terrain_experiment.ipynb
│   └── 08_combined_national_context.ipynb
├── data/
│   └── combined_context/
│       └── CAS_National_Context_enriched.csv
└── results/
```

The `data` and `results` folders contain the datasets and generated outputs used by the notebooks. Some source datasets may be too large for a normal Git repository and can be distributed separately if required.

## Notebook Overview

### 01 — Baseline Modelling

Builds the CAS-only crash-severity baseline, compares machine-learning approaches, evaluates class imbalance, and establishes the modelling framework used in later experiments.

### 02 — Spatial Feature Experiment

Evaluates engineered road-network context, including distance to the nearest derived junction, and contains the separate State Highway contextual analysis.

### 03 — Results Summary

Consolidates the final experimental results, research-question answers, model comparisons, error analysis, SHAP interpretation, and final conclusions.

### 04 — NZDep Experiment

Adds NZDep2023 socioeconomic deprivation information and evaluates its contribution to crash-severity classification.

### 05 — GCH2023 Experiment

Tests geographic classification context. GCH2023 was evaluated during the project but is not included in the final national-context model.

### 06 — Land-Cover Experiment

Adds LCDB land-cover context and evaluates its predictive contribution.

### 07 — Terrain Experiment

Creates and evaluates the LINZ elevation feature used as terrain context.

### 08 — Combined National Context

Reproduces the final paired five-seed comparison between the CAS-only model and the selected national-context model. It also contains the final severe-class error analysis, TreeSHAP interpretation, and leave-one-context-out ablation.

## Final Contextual Predictors

The selected external contextual predictors are:

1. Distance to nearest junction
2. NZDep2023 score
3. LCDB land-cover group
4. Elevation

GCH2023 is not part of the final model.

## Severe-Class Error Analysis

For the seed-42 final-model test set:

- 21.54% of Fatal crashes were predicted exactly as Fatal.
- 46.15% of Fatal crashes were predicted as Serious.
- 39.52% of Serious crashes were predicted exactly as Serious.
- 54.29% of Serious crashes were predicted as Minor or Non-Injury.

These results show that severe-class under-classification remains an important model limitation.

## Model Interpretation

TreeSHAP is used to describe feature contributions to model predictions.

For the final seed-42 model, the highest global mean absolute SHAP contributions include:

1. Distance to junction
2. Motorcycle
3. LCDB land-cover group
4. NZDep2023 score
5. Speed limit

SHAP importance describes model behaviour and does not establish causal relationships.

## Installation

Create a Python environment and install the required packages:

```bash
pip install -r requirements.txt
```

A recent Python 3 version is recommended.

## Running the Notebooks

Start JupyterLab from the project root:

```bash
jupyter lab
```

Open the notebooks in the `Notebook` folder.

The notebooks expect the project `data` folder and its required source/enriched files to remain in the project structure.

## Running the Streamlit Dashboard

From the project root, run:

```bash
streamlit run app.py
```

The dashboard expects this file to exist:

```text
data/combined_context/CAS_National_Context_enriched.csv
```

The dashboard provides:

- crash overview filters by region and year
- contextual-feature visualisations
- final model performance results
- severe-class error analysis
- global SHAP importance
- Fatal and Serious class-specific SHAP interpretation

The Overview and Contextual Features tabs respond to dashboard filters. Model Performance and Model Interpretation display fixed results from the final modelling experiment.

## Reproducibility Notes

The final paired evaluation uses five random seeds:

- 42
- 7
- 21
- 84
- 123

Within each seed, the CAS-only and final-context models use the same stratified train/test split.

Earlier individual context experiments and the final paired national comparison are separate experiment runs and should not be treated as directly cumulative scores.

The State Highway experiment uses a separate crash population and is reported separately from the national model.

## Data Sources

The project uses New Zealand road-crash data together with contextual information derived from project datasets based on sources including:

- New Zealand Crash Analysis System (CAS)
- NZDep2023
- Land Cover Database (LCDB)
- LINZ elevation data
- road-network/junction information

Refer to the project report and notebooks for the full data-source descriptions, preprocessing decisions, licences, and citations.

## Limitations

The final contextual model improves Accuracy and Macro F1 across the evaluated splits, but Balanced Accuracy, Fatal Recall, and Serious Recall are lower than the CAS-only baseline.

The project predicts severity only for already recorded crashes. It should not be interpreted as a crash-risk or crash-occurrence prediction system.

SHAP values describe associations within the fitted model and should not be interpreted as causal effects.
