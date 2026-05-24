"""
field_data_processor.py

This module defines the FieldDataProcessor class, which handles ingestion,
cleaning, transformation, and mapping of field-level agricultural data from
a local SQL database and external weather mapping data.

The class provides methods to:
- Ingest data from an SQLite database.
- Rename or swap column names as specified in a configuration dictionary.
- Apply corrections to certain columns (e.g., absolute values, text replacements).
- Map weather station data from a web-hosted CSV file.
- Log all operations using the built-in Python logging module.

Dependencies:
    - pandas
    - logging
    - data_ingestion (local module)
    - config (local configuration dictionary)

Author: Abdullah Mohamed
Date: 2025-10-06
"""

import pandas as pd
import logging
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
from config import config_params


class FieldDataProcessor:
    """
    A data processing class for managing field data from a SQL database and
    integrating it with external weather mapping data.

    Attributes:
        db_path (str): Path to the SQLite database.
        sql_query (str): SQL query to extract relevant field data.
        columns_to_rename (dict): Dictionary mapping columns to be swapped.
        values_to_rename (dict): Dictionary for replacing incorrect values.
        weather_map_data (str): URL path to the weather station CSV file.
        df (pd.DataFrame): The DataFrame containing ingested field data.
        engine (SQLAlchemy Engine): Database engine for SQL connections.
    """

    def __init__(self, config_params, logging_level="INFO"):
        """
        Initializes the FieldDataProcessor instance.

        Args:
            config_params (dict): Configuration parameters including database path,
                SQL query, renaming rules, and weather mapping source.
            logging_level (str): Logging verbosity level ("DEBUG", "INFO", "NONE").
        """
        self.db_path = config_params['db_path']
        self.sql_query = config_params['sql_query']
        self.columns_to_rename = config_params['columns_to_rename']
        self.values_to_rename = config_params['values_to_rename']
        self.weather_map_data = config_params['weather_csv_path']

        self.df = None
        self.engine = None

        self.initialize_logging(logging_level)

    def initialize_logging(self, logging_level):
        """
        Sets up logging for the FieldDataProcessor instance.

        Args:
            logging_level (str): Desired logging level ("DEBUG", "INFO", "NONE").
        """
        logger_name = __name__ + ".FieldDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False  # Prevent duplicate logs in root logger

        # Set logging level
        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO  # Default to INFO

        self.logger.setLevel(log_level)

        # Avoid adding multiple handlers
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def ingest_sql_data(self):
        """
        Loads data from the configured SQL database into a pandas DataFrame.

        Returns:
            pd.DataFrame: The ingested data.
        """
        self.engine = create_db_engine(self.db_path)
        self.df = query_data(self.engine, self.sql_query)
        self.logger.info("Successfully loaded data from the database.")
        return self.df

    def rename_columns(self):
        """
        Swaps two columns in the DataFrame as specified in the configuration.
        """
        # Extract the columns to rename
        column1, column2 = list(self.columns_to_rename.keys())[0], list(
            self.columns_to_rename.values()
        )[0]

        # Temporary name to prevent conflict
        temp_name = "__temp_name_for_swap__"
        while temp_name in self.df.columns:
            temp_name += "_"

        # Perform the swap
        self.df = self.df.rename(columns={column1: temp_name, column2: column1})
        self.df = self.df.rename(columns={temp_name: column2})

        self.logger.info(f"Swapped columns: {column1} with {column2}")

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):
        """
        Applies data corrections, including:
            - Converting elevation values to their absolute values.
            - Replacing crop type values using a predefined mapping.

        Args:
            column_name (str): Name of the column to apply replacements to.
            abs_column (str): Name of the column for absolute value correction.
        """
        self.df[abs_column] = self.df[abs_column].abs()
        self.df[column_name] = self.df[column_name].apply(
            lambda crop: self.values_to_rename.get(crop, crop)
        )
        self.logger.info("Applied data corrections successfully.")

    def weather_station_mapping(self):
        """
        Loads weather station mapping data from the web.

        Returns:
            pd.DataFrame: The weather mapping data.
        """
        self.logger.info("Loading weather station mapping data...")
        weather_df = read_from_web_CSV(self.weather_map_data)
        self.logger.info("Weather station data loaded successfully.")
        return weather_df

    def process(self):
        """
        Executes the full data processing pipeline:
            1. Load data from the database.
            2. Rename columns.
            3. Apply corrections.
            4. Load weather mapping data.

        Returns:
            tuple: (processed field data DataFrame, weather mapping DataFrame)
        """
        self.ingest_sql_data()
        self.rename_columns()
        self.apply_corrections()
        weather_mapping_df = self.weather_station_mapping()

        self.logger.info("Data processing pipeline completed successfully.")
        return self.df, weather_mapping_df
