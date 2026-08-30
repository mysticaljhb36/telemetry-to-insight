# src/validation.py

from pathlib import Path

import pandas as pd
import yaml


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config():
    """Load project configuration from YAML."""

    config_path = PROJECT_ROOT / "config" / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# development_path = PROJECT_ROOT / load_config()["data"]["development_parquet"]
# df = pd.read_parquet(development_path)

def load_development_data(config):
    """Load the development Parquet dataset."""

    development_path = PROJECT_ROOT / config["data"]["development_parquet"]

    print("Loading development dataset...")

    df = pd.read_parquet(development_path)

    print(f"Dataset loaded: {len(df):,} rows")

    return df

def validate_schema(config, df):
    """
    Validate the structure of the MetroPT-3 development dataset.

    Checks:
    - expected columns are present
    - no unexpected columns exist
    """
  
    # ------------------------------------------------------
    # Expected schema
    # ------------------------------------------------------

    expected_columns = [
        "timestamp",
        "TP2",
        "TP3",
        "H1",
        "DV_pressure",
        "Reservoirs",
        "Oil_temperature",
        "Motor_current",
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses"
    ]

    # ------------------------------------------------------
    # Load development data
    # ------------------------------------------------------

    print("Loading development dataset for schema validation...")


    # ------------------------------------------------------
    # Column validation
    # ------------------------------------------------------

    actual_columns = df.columns.tolist()

    missing_columns = [
        column for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column for column in actual_columns
        if column not in expected_columns
    ]

    print(f"Expected columns: {len(expected_columns)}")
    print(f"Actual columns: {len(actual_columns)}")

    if missing_columns:
        print(f"Missing columns: {missing_columns}")
    else:
        print("No expected columns are missing.")

    if unexpected_columns:
        print(f"Unexpected columns: {unexpected_columns}")
    else:
        print("No unexpected columns detected.")
        
        
def validate_datatypes(df):
    """
    Validate expected datatypes for MetroPT-3 columns.
    """
    
    expected_dtypes = {
        "timestamp": "str",
        "TP2": "float64",
        "TP3": "float64",
        "H1": "float64",
        "DV_pressure": "float64",
        "Reservoirs": "float64",
        "Oil_temperature": "float64",
        "Motor_current": "float64",
        "COMP": "float64",
        "DV_eletric": "float64",
        "Towers": "float64",
        "MPG": "float64",
        "LPS": "float64",
        "Pressure_switch": "float64",
        "Oil_level": "float64",
        "Caudal_impulses": "float64"
    }

    print("\nValidating datatypes...")
    

    datatype_issues = {}

    for column, expected_dtype in expected_dtypes.items():

        actual_dtype = str(df[column].dtype)

        if actual_dtype != expected_dtype:
            datatype_issues[column] = {
                "expected": expected_dtype,
                "actual": actual_dtype
            }

    if datatype_issues:
        print("Datatype issues detected:")

        for column, issue in datatype_issues.items():
            print(
                f"{column}: expected {issue['expected']}, "
                f"found {issue['actual']}"
            )

    else:
        print("All datatypes match the expected schema.")


def validate_nulls(df):
    """
    Check the MetroPT-3 development dataset for missing values.
    """

    print("\nValidating null values...")

    null_counts = df.isnull().sum()

    null_columns = null_counts[null_counts > 0]

    if null_columns.empty:
        print("No null values detected.")

    else:
        print("Null values detected:")

        for column, count in null_columns.items():
            print(f"{column}: {count:,}")


def validate_duplicates(df):
    """
    Check the MetroPT-3 development dataset for duplicate rows.
    """

    print("\nValidating duplicate rows...")

    duplicate_count = df.duplicated().sum()

    if duplicate_count == 0:
        print("No duplicate rows detected.")

    else:
        print(f"Duplicate rows detected: {duplicate_count:,}")
        
        
def validate_duplicate_timestamps(df):
    """
    Check whether multiple records share the same timestamp.
    """

    print("\nValidating duplicate timestamps...")

    duplicate_timestamps = df["timestamp"].duplicated().sum()

    if duplicate_timestamps == 0:
        print("No duplicate timestamps detected.")

    else:
        print(f"Duplicate timestamps detected: {duplicate_timestamps:,}")

def inspect_digital_states(df):
    """
    Inspect observed states of the documented digital sensors
    before defining domain validation rules.
    """

    digital_columns = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level",
        "Caudal_impulses"
    ]

    print("\nInspecting digital sensor states...")

    for column in digital_columns:
        print(f"{column}: {sorted(df[column].unique())}")
   
        
   
def validate_digital_states(df):
    """
    Validate that documented digital control signals contain
    only expected binary states.
    """

    print("\nValidating digital signal states...")

    digital_columns = [
        "COMP",
        "DV_eletric",
        "Towers",
        "MPG",
        "LPS",
        "Pressure_switch",
        "Oil_level"
    ]

    issues_found = False

    for column in digital_columns:

        invalid_values = df.loc[
            ~df[column].isin([0.0, 1.0]),
            column].unique()

        if len(invalid_values) > 0:
            issues_found = True
            print(f"{column}: unexpected states {invalid_values}")

    if not issues_found:
        print("All digital signals contain valid binary states.")
        
        

def validate_timestamp_continuity(df):
    """
    Validate continuity of the MetroPT-3 telemetry timestamps.

    Reports the observed sampling intervals and identifies
    unusually large gaps in the time series.
    """

    print("\nValidating timestamp continuity...")

    timestamps = pd.to_datetime(df["timestamp"]).sort_values()

    time_gaps = timestamps.diff().dropna()

    print(f"Minimum interval: {time_gaps.min()}")
    print(f"Median interval: {time_gaps.median()}")
    print(f"Maximum interval: {time_gaps.max()}")
    
    # Use the median sampling interval as the expected telemetry sequence.
    # Flag gaps greater than twice the median for investigation.
    # Gaps are reported only and are not modified during validation.
    expected_interval = time_gaps.median()

    large_gaps = time_gaps[
        time_gaps > (expected_interval * 2)
    ]

    if large_gaps.empty:
        print("No significant telemetry gaps detected.")
    else:
        print(
            f"Significant telemetry gaps detected: "
            f"{len(large_gaps):,}"
        )
     
        
        
if __name__ == "__main__":

    config = load_config()
    
    df = load_development_data(config)

    validate_schema(config, df)
    
    validate_datatypes(df)
    
    validate_nulls(df)
    
    validate_duplicates(df)
    
    validate_duplicate_timestamps(df)
    
    inspect_digital_states(df)
    
    validate_digital_states(df)
    
    validate_timestamp_continuity(df)