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

# \## Solution Architecture

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

