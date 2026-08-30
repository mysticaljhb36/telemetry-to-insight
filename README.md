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

# \## Data Preparation Pipeline

# 

# \### Ingestion

# \### Validation

# \### Preprocessing

# 

# \## Analytical Approach

# 

# \### Exploratory Analysis

# \### Feature Engineering

# \### Documented Air-Leak Analysis

# 

# \## Key Operational Insight

# 

# \## Running the Project

# 

# \## Current Limitations

# 

# \## Data Attribution

