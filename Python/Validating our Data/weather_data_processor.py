# These are the imports we're going to use in the weather data processing module
"""
weather_data_processor.py
=========================

This module defines the WeatherDataProcessor class, which handles the ingestion,
processing, and summarization of weather station data. It loads raw data from
a web source, extracts measurements using regular expressions, and calculates
mean values per weather station and measurement type.

Classes:
    WeatherDataProcessor: Processes and summarizes weather station data.

Functions:
    - weather_station_mapping(): Loads weather station data from a CSV URL.
    - extract_measurement(): Extracts numeric weather readings using regex patterns.
    - process_messages(): Applies regex extraction across the dataset.
    - calculate_means(): Calculates mean measurement values per station.
    - process(): Orchestrates the entire processing pipeline.

Example:
    >>> from weather_data_processor import WeatherDataProcessor
    >>> from config import config_params
    >>> processor = WeatherDataProcessor(config_params)
    >>> processor.process()
    >>> df = processor.weather_df
    >>> print(df.head())
"""

import re
import numpy as np
import pandas as pd
import logging
from data_ingestion import read_from_web_CSV

class WeatherDataProcessor:
    """
    A class for processing weather station data.

    Attributes:
        weather_station_data (str): URL of the weather data CSV file.
        patterns (dict): Regular expression patterns for extracting weather measurements.
        weather_df (pandas.DataFrame): The DataFrame containing weather data.
        logger (logging.Logger): Logger for class-level logging.
    """
    
    def __init__(self, config_params, logging_level="INFO"): # Now we're passing in the confi_params dictionary already
        """
        Initializes the WeatherDataProcessor with configuration parameters and logging.

        Args:
            config_params (dict): Dictionary containing configuration settings, including:
                - 'weather_csv_path': URL to the weather data CSV.
                - 'regex_patterns': A dictionary of measurement names and regex patterns.
            logging_level (str): Logging verbosity level. Defaults to "INFO".
        """
        self.weather_station_data = config_params['weather_csv_path']
        self.patterns = config_params['regex_patterns']
        self.weather_df = None  # Initialize weather_df as None or as an empty DataFrame
        self.initialize_logging(logging_level)

    def initialize_logging(self, logging_level):
        """
        Configures and initializes a logger for this class instance.

        Args:
            logging_level (str): Logging verbosity level ("DEBUG", "INFO", or "NONE").
        """
        logger_name = __name__ + ".WeatherDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False  # Prevents log messages from being propagated to the root logger

        # Set logging level
        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":  # Option to disable logging
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO  # Default to INFO

        self.logger.setLevel(log_level)

        # Only add handler if not already added to avoid duplicate messages
        if not self.logger.handlers:
            ch = logging.StreamHandler()  # Create console handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def weather_station_mapping(self):
        """
        Loads the weather station data from the provided CSV URL.

        Returns:
            pandas.DataFrame: The loaded weather station dataset.
        """
        self.weather_df = read_from_web_CSV(self.weather_station_data)
        self.logger.info("Successfully loaded weather station data from the web.") 
        # Here, you can apply any initial transformations to self.weather_df if necessary.

    
    def extract_measurement(self, message):
        """
        Extracts a measurement type and value from a message string.

        Args:
            message (str): Text message containing a measurement.

        Returns:
            tuple: (measurement_type, measurement_value)
        """
        for key, pattern in self.patterns.items():
            match = re.search(pattern, message)
            if match:
                self.logger.debug(f"Measurement extracted: {key}")
                return key, float(next((x for x in match.groups() if x is not None)))
        self.logger.debug("No measurement match found.")
        return None, None

    def process_messages(self):
        """
        Applies regex-based extraction on all messages in the weather dataset.

        Returns:
            pandas.DataFrame: DataFrame with added 'Measurement' and 'Value' columns.
        """
        if self.weather_df is not None:
            result = self.weather_df['Message'].apply(self.extract_measurement)
            self.weather_df['Measurement'], self.weather_df['Value'] = zip(*result)
            self.logger.info("Messages processed and measurements extracted.")
        else:
            self.logger.warning("weather_df is not initialized, skipping message processing.")
        return self.weather_df

    def calculate_means(self):
        """
        Calculates mean values of each measurement per weather station.

        Returns:
            pandas.DataFrame: A pivot table of mean measurement values per station.
        """
        if self.weather_df is not None:
            means = self.weather_df.groupby(by=['Weather_station_ID', 'Measurement'])['Value'].mean()
            self.logger.info("Mean values calculated.")
            return means.unstack()
        else:
            self.logger.warning("weather_df is not initialized, cannot calculate means.")
            return None
    
    def process(self):
        """
        Executes the full data processing pipeline.

        Steps:
            1. Loads weather data from the web.
            2. Extracts measurement information using regex.
            3. Logs processing completion.
        """
        self.weather_station_mapping()  # Load and assign data to weather_df
        self.process_messages()  # Process messages to extract measurements
        self.logger.info("Data processing completed.")
