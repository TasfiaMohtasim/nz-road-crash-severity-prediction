# New Zealand Road Crash Severity Prediction

This project uses machine learning to classify the severity of **already recorded road crashes in New Zealand**.

The four classes are:

- Non-Injury
- Minor
- Serious
- Fatal

It does **not** predict whether a crash will happen.

## Final Model

The final model uses **34 predictors**:

- 30 CAS crash variables
- distance to the nearest junction
- NZDep2023 deprivation score
- LCDB land-cover group
- LINZ elevation

### Five-seed results

| Metric | CAS Only | Final Model |
|---|---:|---:|
| Accuracy | 0.4940 | 0.5184 |
| Balanced Accuracy | 0.4062 | 0.3947 |
| Macro F1 | 0.3288 | 0.3389 |
| Fatal Recall | 0.3077 | 0.2215 |
| Serious Recall | 0.3944 | 0.3756 |

Macro F1 improved in all five seeds, with an average gain of **+0.0101**.  
Fatal and Serious crashes were still difficult to classify, so severe-crash prediction remains an important limitation.

## Project Structure

```text
Project_Roadcrash/
├── app.py
├── README.md
├── DATA_SOURCES.md
├── requirements.txt
├── Notebook/
├── data/
└── results/
```

The `Notebook` folder contains the eight project notebooks, from the CAS baseline through to the final combined national-context model.

Large geospatial files are stored using **Git LFS**.

## Run the Project

Install the packages:

```bash
pip install -r requirements.txt
```

Open the notebooks:

```bash
jupyter lab
```

Run the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard uses:

```text
data/combined_context/CAS_National_Context_enriched.csv
```

## Data Sources

The project uses public datasets from NZ Transport Agency Waka Kotahi, University of Otago, Stats NZ, Manaaki Whenua - Landcare Research, and Toitū Te Whenua LINZ.

See **[DATA_SOURCES.md](DATA_SOURCES.md)** for the source links and licence information.

## Notes

- GCH2023 was tested in a separate experiment but was not included in the final model.
- The derived GCH-enriched CSV is not redistributed in this repository.
- SHAP values explain model behaviour; they do not prove causation.
- Third-party datasets remain subject to their original provider licences.

## Live Dashboard

Interactive Streamlit dashboard:

https://nz-road-crash-severity-app.streamlit.app/
