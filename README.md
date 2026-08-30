# \# Telemetry-to-Insight: MetroPT-3 Air Compressor Analysis

# 

# \## Overview

# 

# This project presents an end-to-end \*\*telemetry-to-insight\*\* exploration of the MetroPT-3 railway air-compressor dataset.

# 

# The proof of concept demonstrates how operational telemetry can be ingested, validated, prepared and analysed to derive interpretable indicators of compressor workload and operating behaviour.

# 

# The analysis focuses on:

# 

# \- compressor loaded-state utilisation;

# \- load-cycle frequency;

# \- loaded-cycle duration; and

# \- supporting pressure and motor-current behaviour.

# 

# These operational features are evaluated against documented air-leak periods to investigate whether the telemetry reveals developing or persistent changes in compressor workload that could support engineering investigation and condition monitoring.

# 

# The primary analytical deliverable is:

# 

# `notebooks/telemetry\_insight.ipynb`



# 

# \## Customer / Operational Question

# 

# The analysis investigates whether changes in railway air-compressor telemetry can reveal meaningful changes in operating behaviour around documented air-leak periods.

# 

# The central operational question is:

# 

# > \*\*Can compressor telemetry identify developing or persistent changes in workload that may warrant engineering investigation?\*\*

# 

# Rather than assuming that elevated compressor activity represents a specific failure, the analysis focuses on observable changes in asset behaviour and the operational context surrounding them.

# 

# This provides a basis for considering how telemetry-derived indicators could support \*\*condition monitoring, maintenance prioritisation and engineering decision-making\*\*.

# 

# \## Project Scope

# 

# This proof of concept demonstrates an end-to-end workflow for transforming operational railway air-compressor telemetry into interpretable engineering insight.

# 

# The project covers:

# 

# \- ingestion and preparation of the public MetroPT-3 telemetry dataset;

# \- validation of data quality, structure and temporal characteristics;

# \- exploratory analysis of compressor operating behaviour;

# \- domain-led feature engineering focused on compressor workload and cycling;

# \- comparison of engineered operational metrics against documented air-leak periods; and

# \- development of an interpretable operational insight that could support condition monitoring and engineering investigation.

# 

# The analysis is exploratory and does not attempt to assign a specific failure cause from telemetry alone. Documented air-leak periods are used as external reference windows against which observed compressor behaviour can be evaluated.

# 

# \## Dataset

# 

# This project uses the \*\*MetroPT-3\*\* dataset from the UCI Machine Learning Repository. The dataset contains operational telemetry collected from the \*\*Air Production Unit (APU) of a metropolitan train\*\* between February and August 2020.

# 

# The telemetry contains analogue measurements and digital control-state signals associated with compressor operation, including pressure, temperature, motor current and air-intake/control states.

# 

# Key signals used within this analysis include:

# 

# | Signal | Description / Analytical Role |

# |---|---|

# | `TP2` | Compressor pressure (bar) |

# | `Motor\_current` | Compressor motor current |

# | `DV\_eletric` | Digital state indicating loaded compressor operation |

# | `COMP` | Compressor operating/control-state signal |

# | `MPG` | Compressor control-state signal |

# 

# Additional telemetry signals are retained within the processed dataset and used where necessary to understand the wider operating context.

# 

# \### Development Period

# 

# For iterative development and analysis, a subset covering \*\*1 March to 31 July 2020\*\* was extracted from the source dataset.

# 

# The development dataset contains \*\*1,081,134 observations\*\* and includes:

# 

# \- operating history before the first documented air-leak period;

# \- all four documented air-leak periods used as reference windows; and

# \- operating history following the final documented event.

# 

# Using this development period reduced the volume of data repeatedly processed during exploratory development while retaining the operational periods required for the proof of concept.

# 

# Validation of the actual telemetry timestamps identified a \*\*typical sampling interval of approximately 10 seconds\*\*. Larger gaps were also observed and are retained rather than reconstructed or imputed.

# 

# \## Solution Architecture

# 

# The solution separates reusable data-preparation logic from exploratory analysis and visualisation.

# 

# The end-to-end workflow is:

# 

# \*\*Public MetroPT-3 Telemetry → Ingestion → Development Dataset → Validation → Preprocessing → Exploratory Analysis → Feature Engineering → Operational Insight\*\*

# 

# The project is organised around three main layers:

# 

# 1\. \*\*Configuration and data preparation\*\*  

# &#x20;  Project configuration defines source locations, local data paths and the development period. Reusable Python modules handle ingestion, validation and preprocessing.

# 

# 2\. \*\*Pipeline orchestration\*\*  

# &#x20;  The root-level `run.py` script coordinates the data-preparation stages, providing a single entry point for preparing the telemetry required by the analysis.

# 

# 3\. \*\*Analysis and insight\*\*  

# &#x20;  `notebooks/telemetry\_insight.ipynb` consumes the processed telemetry and contains the exploratory analysis, domain-led feature engineering, interactive visualisation and interpretation of compressor operating behaviour.

# 

# This separation keeps the repeatable data-preparation workflow outside the notebook while retaining the notebook as a transparent analytical environment for investigating the telemetry and communicating the resulting insight.

# 

# \## Project Structure

# 

# The repository separates configuration, data, reusable source code, analytical work and automated tests into distinct directories.

# 

# ```text

# telemetry-to-insight/

# ├── README.md

# ├── requirements.txt

# ├── environment.yml

# ├── .gitignore

# ├── run.py

# │

# ├── config/

# │   └── config.yaml

# │

# ├── data/

# │   ├── raw/

# │   ├── development/

# │   ├── processed/

# │   └── README.md

# │

# ├── notebooks/

# │   └── telemetry\_insight.ipynb

# │

# ├── src/

# │   ├── \_\_init\_\_.py

# │   ├── ingestion.py

# │   ├── validation.py

# │   ├── preprocessing.py

# │   ├── features.py

# │   └── visualisation.py

# │

# └── tests/

# &#x20;   ├── test\_features.py

# &#x20;   └── test\_validation.py

# ```

# 

# The main components are:

# 

# \- \*\*`config/`\*\* – project configuration, including data-source and development-period settings.

# \- \*\*`data/`\*\* – local storage for raw, development and processed telemetry datasets.

# \- \*\*`src/`\*\* – reusable Python modules supporting ingestion, validation, preprocessing, feature engineering and visualisation.

# \- \*\*`notebooks/`\*\* – the primary analytical notebook used for telemetry exploration, feature development, visualisation and insight generation.

# \- \*\*`tests/`\*\* – automated tests for reusable project functionality.

# \- \*\*`run.py`\*\* – root-level entry point that orchestrates the data-preparation pipeline.

# 

# Telemetry data files are kept outside version control so that the repository remains lightweight and the source data can be reproduced through the ingestion workflow.

# 

# \## Data Preparation Pipeline

# 

# The reusable data-preparation workflow is orchestrated by `run.py` and implemented through modules within `src/`. The pipeline prepares a consistent telemetry dataset for downstream analysis while keeping data engineering logic separate from the analytical notebook.

# 

# \### Ingestion

# 

# The ingestion stage is implemented in `src/ingestion.py` and uses settings defined in `config/config.yaml`.

# 

# The workflow:

# 

# \- downloads the public MetroPT-3 source archive when the raw dataset is not already available locally;

# \- reads the source CSV from the compressed archive;

# \- converts the raw telemetry to \*\*Parquet\*\* for more efficient subsequent storage and access;

# \- extracts the configured development period from the raw dataset; and

# \- stores the resulting development dataset separately from the original raw telemetry.

# 

# Both the raw Parquet dataset and development extract are reused when already available, avoiding unnecessary repeated downloads and processing during iterative development.

# 

# The development extract is created using Parquet filtering against the configured date range, allowing the proof of concept to work with the required operational period without repeatedly loading the complete source dataset into the analytical workflow.

# 

# \### Validation

# 

# The validation stage is implemented in `src/validation.py` and is applied to the development dataset before preprocessing and analysis.

# 

# The current validation workflow checks:

# 

# \- expected telemetry columns and unexpected fields;

# \- data types;

# \- missing values;

# \- duplicate rows;

# \- duplicate timestamps;

# \- observed states of digital telemetry signals;

# \- whether documented digital signals contain only expected binary states; and

# \- timestamp continuity and unusually large gaps between observations.

# 

# Validation identified no missing values, duplicate rows or duplicate timestamps within the development dataset. The digital signals evaluated as binary contained only `0` and `1` states.

# 

# An additional source column, `Unnamed: 0`, was identified during schema validation and is subsequently removed during preprocessing.

# 

# \### Temporal Continuity

# 

# Analysis of consecutive timestamps showed a \*\*median interval of approximately 10 seconds\*\*, consistent with the typical interval observed in the development telemetry.

# 

# However, \*\*267 intervals exceeded twice the median sampling interval\*\*, with the largest observed gap being approximately \*\*two days\*\*.

# 

# These gaps are retained rather than reconstructed or imputed because their cause cannot be determined from the telemetry alone. They may reflect operational downtime, connectivity issues, maintenance or other system behaviour.

# 

# Preserving these gaps also avoids introducing artificial telemetry states into subsequent operational analysis.



# 

# \### Preprocessing

# 

# The preprocessing stage is implemented in `src/preprocessing.py` and prepares the validated development telemetry for downstream analysis.

# 

# The workflow:

# 

# \- removes the redundant `Unnamed: 0` source column identified during schema validation;

# \- converts `timestamp` to a datetime representation, raising an error if conversion fails;

# \- sorts observations chronologically by timestamp;

# \- resets the DataFrame index following sorting; and

# \- stores the prepared dataset in \*\*Parquet\*\* format for use by the analytical notebook.

# 

# The preprocessing stage intentionally avoids imputing missing timestamps or reconstructing gaps in the telemetry. This preserves the observed temporal behaviour of the source data and prevents artificial observations from being introduced into subsequent feature engineering and operational analysis.

# 

# The resulting processed dataset provides the consistent chronological input used by `notebooks/telemetry\_insight.ipynb`.

# 

# \## Analytical Approach

# 

# The analysis follows a domain-led approach, using the documented behaviour of the air-compressor system to determine which telemetry signals and derived metrics are operationally meaningful.

# 

# Rather than generating a large number of arbitrary statistical features, the analysis progressively moves from understanding normal compressor behaviour to evaluating changes in workload around documented air-leak periods.

# 

# \### Exploratory Analysis

# 

# Initial exploratory analysis was used to understand the operating relationships between the compressor's analogue measurements and digital control states before engineering higher-level operational metrics.

# 

# The exploration focused particularly on:

# 

# \- `DV\_eletric` as an indicator of when the compressor is operating under load;

# \- `Motor\_current` to understand electrical behaviour across compressor operating states;

# \- `TP2` and supporting pressure signals to understand compressor pressure behaviour; and

# \- digital control signals such as `COMP` and `MPG` to understand compressor operating transitions.

# 

# This established the operational context required to interpret subsequent features rather than treating individual telemetry signals independently.

# 

# The exploratory analysis also showed that motor current while the compressor was loaded remained relatively stable across much of the development period. This shifted the analytical focus towards \*\*how often and how long the compressor was required to operate under load\*\*, rather than treating loaded motor-current magnitude alone as the primary indicator of changing workload.

# 

# \### Feature Engineering

# 

# Feature engineering translates the raw compressor control states into operational metrics that are easier to interpret from a condition-monitoring perspective.

# 

# The analysis focuses on three complementary aspects of compressor workload:

# 

# \- \*\*Loaded utilisation\*\* – the proportion of observed telemetry samples for which `DV\_eletric = 1`, representing the amount of observed time the compressor operates under load.

# \- \*\*Load-cycle frequency\*\* – the number of transitions into the loaded state, providing an indication of how frequently the compressor is required to begin loaded operation.

# \- \*\*Loaded-cycle duration\*\* – the elapsed time associated with individual loaded operating cycles, providing context on whether workload is driven by repeated cycling, sustained loaded operation, or a combination of both.

# 

# A cumulative `load\_cycle\_id` is used to identify individual loaded cycles and provide traceability when investigating specific operating periods.

# 

# \### Rolling Workload Indicator

# 

# In addition to daily operational metrics, a causal \*\*30-minute rolling loaded-utilisation\*\* feature was developed to retain short-term temporal context that daily aggregation can obscure.

# 

# The rolling metric uses only current and preceding observations, allowing changes in recent compressor workload to be examined through time without incorporating future telemetry.

# 

# The 30-minute interval is an exploratory monitoring window rather than an assumed optimal threshold. It provides sufficient smoothing to expose sustained changes in workload while retaining considerably more temporal resolution than daily aggregation.

# 

# Together, these features allow compressor behaviour to be interpreted across three dimensions:

# 

# \*\*How much is it working? → How often is it cycling? → How long does each loaded period persist?\*\*

# 

# \### Documented Air-Leak Analysis

# 

# The engineered workload metrics were evaluated against four documented air-leak periods provided with the MetroPT-3 dataset.

# 

# These periods are treated as \*\*external reference windows rather than telemetry labels\*\*. The analysis therefore compares observed compressor behaviour around the documented periods without assuming that every change in workload represents an air leak.

# 

# The analysis combines:

# 

# \- raw telemetry inspection around the documented events;

# \- daily loaded utilisation and load-cycle frequency;

# \- individual loaded-cycle duration;

# \- the 30-minute rolling loaded-utilisation indicator; and

# \- supporting pressure and motor-current behaviour.

# 

# Across the four documented air-leak periods, the rolling workload indicator showed sustained increases in loaded compressor operation and reached very high utilisation during each event window.

# 

# However, a separate high-utilisation episode on \*\*28–29 March 2020\*\*, outside the documented air-leak periods, exhibited similar sustained workload behaviour.

# 

# This counterexample is important because it demonstrates that elevated loaded utilisation is \*\*not specific to a documented air leak\*\*. Instead, it should be interpreted as an indicator of abnormal or sustained compressor workload whose underlying cause requires additional operational context or engineering investigation.

# 

# The comparison therefore focuses on identifying meaningful changes in compressor operating behaviour rather than assigning a failure class directly from the telemetry.

# 

# \## Key Operational Insight

# 

# The analysis indicates that compressor telemetry can identify \*\*developing and persistent changes in workload that may warrant engineering investigation\*\*, without assuming the underlying cause.

# 

# During all four documented air-leak periods, the 30-minute rolling loaded-utilisation indicator developed into sustained high compressor utilisation and reached \*\*100% within the first hour of the documented event window\*\*.

# 

# The supporting operational features provide additional context:

# 

# \- \*\*loaded utilisation\*\* captures the overall proportion of observed time spent operating under load;

# \- \*\*load-cycle frequency\*\* distinguishes frequent cycling from sustained operation; and

# \- \*\*loaded-cycle duration\*\* identifies periods where the compressor remains continuously loaded for unusually long durations.

# 

# Motor current during loaded operation remained comparatively stable across much of the development period. This suggests that changes in operational burden are better characterised by \*\*how frequently and how persistently the compressor operates under load\*\*, rather than loaded motor-current magnitude alone.

# 

# Importantly, the high-utilisation episode observed on \*\*28–29 March 2020\*\* demonstrates that sustained compressor workload is not uniquely associated with the documented air-leak periods.

# 

# The resulting customer insight is therefore:

# 

# > \*\*Sustained changes in compressor workload can provide an interpretable condition-monitoring signal for identifying periods that may warrant engineering investigation, but workload behaviour alone is insufficient to determine the underlying fault.\*\*

# 

# In an operational monitoring system, this type of workload indicator could be combined with persistence, cycle-duration and pressure context to prioritise periods for engineering review.

# 

# \## Running the Project

# 

# \### 1. Create the Environment

# 

# The project includes both `environment.yml` and `requirements.txt` for dependency management.

# 

# Using Conda:

# 

# ```bash

# conda env create -f environment.yml

# conda activate metropt-iot

# ```

# 

# Alternatively, using `pip` within an existing Python environment:

# 

# ```bash

# pip install -r requirements.txt

# ```

# 

# Ensure the project environment is active before running the data-preparation pipeline.

# 

# \### 2. Prepare the Telemetry Data

# 

# Ensure the project environment is active before running the data-preparation pipeline.

# 

# From the project root, the pipeline can be executed from the command line:

# 

# ```bash

# python run.py

# ```

# 

# Alternatively, open the project in your preferred Python IDE, open `run.py`, ensure the configured project environment/interpreter is selected, and run the script directly.

# 

# The pipeline uses the settings in `config/config.yaml` to:

# 

# 1\. ingest the MetroPT-3 source data;

# 2\. create the configured development extract;

# 3\. validate the development telemetry; and

# 4\. preprocess and save the dataset required for analysis.

# 

# Existing raw and development datasets are reused where applicable to avoid unnecessary repeated ingestion work.

# 

# \### 3. Run the Analysis

# 

# After the data-preparation pipeline has completed, open:

# 

# ```text

# notebooks/telemetry\_insight.ipynb

# ```

# 

# Run the notebook from top to bottom to reproduce the exploratory analysis, engineered operational features, interactive visualisations and resulting telemetry insight.

# 

# The intended execution flow is therefore:

# 

# \*\*Environment → `run.py` → Processed Telemetry → `telemetry\_insight.ipynb` → Operational Insight\*\*

# 

# \## Current Limitations

# 

# \## Data Attribution

