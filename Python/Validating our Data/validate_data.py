# !pip install pytest

import re
import numpy as np
import pandas as pd
from field_data_processor import FieldDataProcessor
from weather_data_processor import WeatherDataProcessor
import logging
from config import config_params

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

field_processor = FieldDataProcessor(config_params)
field_processor.process()
field_df = field_processor.df

weather_processor = WeatherDataProcessor(config_params)
weather_processor.process()
weather_df = weather_processor.weather_df

weather_df.to_csv('sampled_weather_df.csv', index=False)
field_df.to_csv('sampled_field_df.csv', index=False)

#!pytest validate_data.py -v

import os# Define the file paths
weather_csv_path = 'sampled_weather_df.csv'
field_csv_path = 'sampled_field_df.csv'

# Delete sampled_weather_df.csv if it exists
if os.path.exists(weather_csv_path):
    os.remove(weather_csv_path)
    print(f"Deleted {weather_csv_path}")
else:
    print(f"{weather_csv_path} does not exist.")

# Delete sampled_field_df.csv if it exists
if os.path.exists(field_csv_path):
    os.remove(field_csv_path)
    print(f"Deleted {field_csv_path}")
else:
    print(f"{field_csv_path} does not exist.")