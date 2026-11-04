import pandas as pd
from pathlib import Path
from ingestion_proposed import PROJECT_ROOT, load_config

config = load_config()
path = PROJECT_ROOT / config["data"]["development_parquet"]

development_df = pd.read_parquet(path)
print(development_df.head(10))