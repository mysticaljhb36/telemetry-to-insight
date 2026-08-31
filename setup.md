# Telemetry-to-Insight — Setup Guide

This guide explains how to set up and reproduce the Telemetry-to-Insight project from a fresh clone.

The source telemetry dataset is not stored in this repository. When required, the data-preparation pipeline retrieves the public MetroPT-3 dataset from the UCI Machine Learning Repository and creates the local datasets required for the analysis.

---

## 1. Clone the Repository

```bash
git clone https://github.com/mysticaljhb36/telemetry-to-insight
cd telemetry-to-insight
```

## 2. Create and Activate the Conda Environment

```bash
conda env create -f environment.yml
conda activate telemetry-to-insight
```

The environment name is defined in `environment.yml`.

Alternatively, dependencies can be installed into an existing Python environment:

```bash
pip install -r requirements.txt
```

## 3. Run the Data-Preparation Pipeline

From the project root:

```bash
python run.py
```

The pipeline:

- retrieves and persists the source telemetry when required;
- creates the configured development extract;
- validates the telemetry;
- preprocesses the dataset; and
- records runtime activity in `logs/pipeline.log`.

Existing raw and development datasets are reused when available.

On a fresh clone, the required local data assets will therefore be created automatically when the pipeline is run.

## 4. Launch the Analysis

```bash
jupyter notebook
```

Open:

```text
notebooks/telemetry_insight.ipynb
```

Run the notebook from top to bottom to reproduce the exploratory analysis, engineered operational features, interactive visualisations and resulting operational insight.

---

## Reproduction Workflow

**Clone → Environment → `run.py` → Processed Telemetry → `telemetry_insight.ipynb` → Operational Insight**