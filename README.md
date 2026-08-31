# Telemetry-to-Insight: MetroPT-3 Air Compressor Analysis

## Getting Started

To reproduce the project from a fresh clone, see the **[Setup Guide](https://github.com/mysticaljhb36/telemetry-to-insight/blob/master/setup.md)**.

**Repository:** [telemetry-to-insight](https://github.com/mysticaljhb36/telemetry-to-insight)

## Overview

This project presents an end-to-end **telemetry-to-insight** exploration of the MetroPT-3 railway air-compressor dataset.

The proof of concept demonstrates how operational telemetry can be ingested, validated, prepared and analysed to derive interpretable indicators of compressor workload and operating behaviour.

The analysis focuses on:

- compressor loaded-state utilisation;
- load-cycle frequency;
- loaded-cycle duration; and
- supporting pressure and motor-current behaviour.

These operational features are evaluated against documented air-leak periods to investigate whether the telemetry reveals developing or persistent changes in compressor workload that could support engineering investigation and condition monitoring.

The primary analytical deliverable is `notebooks/telemetry_insight.ipynb`.

## Customer / Operational Question

The central operational question is:

> **Can compressor telemetry identify developing or persistent changes in workload that may warrant engineering investigation?**

Rather than assuming that elevated compressor activity represents a specific failure, the analysis focuses on observable changes in asset behaviour and the operational context surrounding them. This provides a basis for considering how telemetry-derived indicators could support **condition monitoring, maintenance prioritisation and engineering decision-making**.

## Project Scope

This proof of concept covers:

- ingestion and preparation of the public MetroPT-3 telemetry dataset;
- validation of data quality, structure and temporal characteristics;
- exploratory analysis of compressor operating behaviour;
- domain-led feature engineering focused on compressor workload and cycling;
- comparison of engineered operational metrics against documented air-leak periods; and
- development of an interpretable operational insight that could support condition monitoring and engineering investigation.

The analysis is exploratory and does not attempt to assign a specific failure cause from telemetry alone. Documented air-leak periods are used as external reference windows against which observed compressor behaviour can be evaluated.

## Dataset

This project uses the **MetroPT-3** dataset from the UCI Machine Learning Repository. The dataset contains operational telemetry collected from the **Air Production Unit (APU) of a metropolitan train** between February and August 2020.

Key signals used within this analysis include:

| Signal | Description / Analytical Role |
|---|---|
| `TP2` | Compressor pressure (bar) |
| `Motor_current` | Compressor motor current |
| `DV_eletric` | Digital state indicating loaded compressor operation |
| `COMP` | Compressor operating/control-state signal |
| `MPG` | Compressor control-state signal |

Additional telemetry signals are retained within the processed dataset and used where necessary to understand the wider operating context.

### Development Period

For iterative development and analysis, a subset covering **1 March to 31 July 2020** was extracted from the source dataset.

The development dataset contains **1,081,134 observations** and includes operating history before the first documented air-leak period, all four documented air-leak periods used as reference windows, and operating history following the final documented event.

Using this development period reduced the volume of data repeatedly processed during exploratory development while retaining the operational periods required for the proof of concept.

Validation of the actual telemetry timestamps identified a **typical sampling interval of approximately 10 seconds**. Larger gaps were also observed and are retained rather than reconstructed or imputed.

## Solution Architecture

The solution separates reusable data-preparation logic from exploratory analysis, feature engineering and visualisation.

**Public MetroPT-3 Telemetry → Ingestion → Development Dataset → Validation → Preprocessing → Processed Telemetry → Exploratory Analysis → Feature Engineering → Operational Insight**

The project is organised around three main layers:

1. **Configuration and data preparation** – `config/config.yaml` defines the source, local data paths, ingestion settings and development period. Reusable Python modules handle ingestion, validation and preprocessing.
2. **Pipeline orchestration and observability** – `run.py` provides the single data-preparation entry point. `src/logger.py` configures application logging, with runtime activity written to `logs/pipeline.log`.
3. **Analysis and insight** – `notebooks/telemetry_insight.ipynb` consumes the processed telemetry and contains exploratory analysis, domain-led feature engineering, interactive visualisation and interpretation.

This separation keeps repeatable data-preparation logic outside the notebook while retaining the notebook as a transparent analytical environment.

## Project Structure

```text
telemetry-to-insight/
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
├── run.py
├── config/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── development/
│   ├── processed/
│   └── README.md
├── logs/
│   └── pipeline.log
├── notebooks/
│   └── telemetry_insight.ipynb
└── src/
    ├── __init__.py
    ├── logger.py
    ├── ingestion.py
    ├── validation.py
    └── preprocessing.py
```

`pipeline.log` and generated telemetry files exist locally at runtime but are excluded from version control.

## Data Preparation Pipeline

The reusable data-preparation workflow is orchestrated by `run.py` and implemented through modules within `src/`.

### Ingestion

`src/ingestion.py`:

- downloads the public MetroPT-3 source archive when the raw dataset is not already available locally;
- reads the source CSV from the compressed archive;
- persists raw telemetry as **Parquet** for efficient repeated access;
- extracts the configured development period; and
- stores the development dataset separately from the raw telemetry.

Raw and development datasets are reused when already available, avoiding unnecessary repeated downloads and processing during iterative development.

### Validation

`src/validation.py` checks:

- expected telemetry columns and genuinely unexpected fields;
- compatible data types;
- missing values;
- duplicate rows;
- duplicate timestamps;
- observed states of digital telemetry signals;
- documented binary control states; and
- timestamp continuity and unusually large gaps.

Critical structural and data-quality failures stop the pipeline. Timestamp gaps are reported as warnings because genuine breaks in the observed telemetry are retained rather than reconstructed.

Validation identified no missing values, duplicate rows or duplicate timestamps. The documented binary control signals contained only `0` and `1` states.

The source-generated `Unnamed: 0` field is recognised as an allowed source artefact during validation and intentionally removed during preprocessing.

### Temporal Continuity

Consecutive timestamps showed a **median interval of approximately 10 seconds**. **267 intervals exceeded twice the median sampling interval**, with the largest observed gap being approximately **two days**.

These gaps are retained because their cause cannot be determined from the telemetry alone. Preserving them avoids introducing artificial telemetry states.

### Preprocessing

`src/preprocessing.py`:

- removes the known `Unnamed: 0` source artefact;
- converts `timestamp` to datetime, raising an error if conversion fails;
- sorts observations chronologically;
- resets the DataFrame index; and
- persists the analysis-ready dataset as **Parquet**.

No missing timestamp periods are imputed or reconstructed. The resulting processed dataset contains **1,081,134 observations** and is consumed by `notebooks/telemetry_insight.ipynb`.

### Logging and Failure Behaviour

Logging is configured centrally in `src/logger.py`. Individual modules use named loggers so messages identify their source.

The pipeline records stage execution, ingestion and local-data reuse, validation outcomes, telemetry continuity warnings, preprocessing, persistence, successful completion and failures.

Critical validation failures raise exceptions and stop execution. At the orchestration boundary, `run.py` logs the failure and traceback before re-raising the exception.

Runtime logs are appended to `logs/pipeline.log`. The logging directory is created automatically when required, and `.log` files are excluded from version control.

## Analytical Approach

The notebook follows a domain-led approach, using documented compressor behaviour to determine which signals and derived metrics are operationally meaningful rather than generating arbitrary statistical features.

### Exploratory Analysis

Exploration focuses particularly on:

- `DV_eletric` as an indicator of loaded compressor operation;
- `Motor_current` across operating states;
- `TP2` and supporting pressure signals; and
- control signals such as `COMP` and `MPG`.

Loaded motor current remained comparatively stable across much of the development period. This shifted the focus toward **how often and how long the compressor was required to operate under load**.

### Feature Engineering

Feature engineering is performed transparently within `notebooks/telemetry_insight.ipynb`.

The principal workload metrics are:

- **Loaded utilisation** – proportion of observed samples for which `DV_eletric = 1`.
- **Load-cycle frequency** – number of transitions into the loaded state.
- **Loaded-cycle duration** – elapsed time associated with individual loaded operating cycles.

A cumulative `load_cycle_id` provides traceability when investigating individual loaded cycles.

### Rolling Workload Indicator

A causal **30-minute rolling loaded-utilisation** feature retains short-term temporal context that daily aggregation can obscure.

The metric uses only current and preceding observations. The 30-minute interval is an exploratory monitoring window rather than an assumed optimal threshold.

Together, the features address:

**How much is it working? → How often is it cycling? → How long does each loaded period persist?**

### Documented Air-Leak Analysis

The workload metrics are evaluated against four documented air-leak periods supplied with the MetroPT-3 dataset.

These periods are treated as **external reference windows rather than telemetry labels**. The analysis combines raw telemetry inspection, daily loaded utilisation, load-cycle frequency, individual loaded-cycle duration, causal rolling utilisation, and supporting pressure and motor-current behaviour.

Across all four documented periods, the rolling workload indicator showed sustained increases in loaded compressor operation and reached very high utilisation during each event window.

The evidence therefore supports interpreting sustained workload as a useful **condition-monitoring indicator**, while fault attribution requires additional operational context and engineering validation.

## Key Operational Insight

During all four documented air-leak periods, the 30-minute rolling loaded-utilisation indicator developed into sustained high compressor utilisation and reached **100% within the first hour of the documented event window**.

Loaded utilisation captures **how much** the compressor works, load-cycle frequency provides context on **how often** it enters loaded operation, and loaded-cycle duration shows **how long** loaded operation persists.

Motor current during loaded operation remained comparatively stable across much of the development period, suggesting that changes in operational burden are better characterised by workload frequency and persistence than by loaded motor-current magnitude alone.

> **Sustained changes in compressor workload can provide an interpretable condition-monitoring signal for identifying periods that may warrant engineering investigation, but workload behaviour alone is insufficient to determine the underlying fault.**

In an operational monitoring system, this type of workload indicator could be combined with persistence, cycle-duration and pressure context to prioritise periods for engineering review.

## Current Limitations

This proof of concept is based on a single public railway air-compressor telemetry dataset and should be interpreted as an exploratory condition-monitoring analysis rather than a production diagnostic system.

Key limitations include:

- **External reference windows** – documented air-leak periods are operational reference windows rather than observation-level failure labels.
- **Telemetry gaps** – larger timestamp gaps are retained rather than imputed because their causes are unknown and may affect cycle-duration calculations.
- **Workload is not fault-specific** – elevated or sustained compressor workload alone is insufficient to diagnose an air leak or other specific fault.
- **Rolling interval selection** – the 30-minute interval is exploratory rather than optimised. Other intervals may provide different responsiveness/sensitivity trade-offs.
- **Single-asset analysis** – the analysis does not establish whether monitoring parameters generalise across other compressors or train assets.

Further development should evaluate monitoring parameters across longer operating histories and multiple comparable assets, incorporating maintenance records and engineering knowledge to determine whether thresholds should be asset-specific or transferable across similar equipment.

A potential production extension would evaluate robust change detection and persistence-based monitoring against recent operating baselines, with thresholds calibrated from recent historical behaviour and engineering evidence rather than assumed in advance.

## Data Attribution

This project uses the **MetroPT-3** dataset made publicly available through the UCI Machine Learning Repository.

**Dataset:** MetroPT-3  
**Repository:** UCI Machine Learning Repository  
**Source:** https://archive.ics.uci.edu/dataset/791/metropt+3+dataset

The dataset contains operational telemetry collected from the Air Production Unit (APU) of a metropolitan train.

The original telemetry data and locally generated development and processed datasets are excluded from version control. The project ingestion workflow can retrieve and prepare the source data required to reproduce the analysis.
