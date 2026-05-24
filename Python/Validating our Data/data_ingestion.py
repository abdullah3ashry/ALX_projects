"""
data_ingestion.py

This module provides utility functions for ingesting and loading data from multiple
sources including:
    - SQL databases (via SQLAlchemy)
    - Remote CSV files hosted on the web

The module also implements structured logging for debugging and monitoring data ingestion
operations. It serves as a helper module for the FieldDataProcessor and WeatherDataProcessor
classes, providing reliable methods for data loading and validation.

Functions:
    - create_db_engine(db_path): Creates and tests a connection to a database.
    - query_data(engine, sql_query): Executes an SQL query and returns the results as a DataFrame.
    - read_from_web_CSV(URL): Reads a CSV file from a remote web source.

Dependencies:
    - SQLAlchemy
    - pandas
    - logging
    - config (local configuration dictionary)

Author: Abdullah Mohamed
Date: 2025-10-06
"""

from sqlalchemy import create_engine, text
import logging
import pandas as pd
from config import config_params

# --------------------------------------------------------------------------------
# LOGGING SETUP
# --------------------------------------------------------------------------------

# Create and configure logger for this module
logger = logging.getLogger('data_ingestion')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# --------------------------------------------------------------------------------
# DATABASE CONNECTION FUNCTIONS
# --------------------------------------------------------------------------------

def create_db_engine(db_path):
    """
    Creates and tests a SQLAlchemy database engine.

    Args:
        db_path (str): Path to the database or database connection string.
                       Example: "sqlite:///data/agriculture.db"

    Returns:
        sqlalchemy.engine.Engine: SQLAlchemy engine object for database interaction.

    Raises:
        ImportError: If SQLAlchemy is not installed.
        Exception: If the connection test or engine creation fails.
    """
    try:
        engine = create_engine(db_path)
        # Test connection
        with engine.connect() as conn:
            pass
        logger.info("Database engine created successfully.")
        return engine

    except ImportError:
        logger.error("SQLAlchemy is required to use this function. Please install it first.")
        raise

    except Exception as e:
        logger.error(f"Failed to create database engine. Error: {e}")
        raise


def query_data(engine, sql_query):
    """
    Executes a SQL query using a given SQLAlchemy engine and returns the result as a DataFrame.

    Args:
        engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        sql_query (str): SQL query to execute.

    Returns:
        pandas.DataFrame: DataFrame containing the query results.

    Raises:
        ValueError: If the query returns an empty DataFrame.
        Exception: If any other SQL or connection error occurs.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection)

        if df.empty:
            msg = "The query returned an empty DataFrame."
            logger.error(msg)
            raise ValueError(msg)

        logger.info("Query executed successfully.")
        return df

    except ValueError as e:
        logger.error(f"SQL query returned no data. Error: {e}")
        raise

    except Exception as e:
        logger.error(f"An error occurred while querying the database. Error: {e}")
        raise


# --------------------------------------------------------------------------------
# WEB DATA INGESTION FUNCTION
# --------------------------------------------------------------------------------

def read_from_web_CSV(URL):
    """
    Reads a CSV file directly from a given URL.

    Args:
        URL (str): Web URL pointing to a CSV file.

    Returns:
        pandas.DataFrame: DataFrame containing the CSV data.

    Raises:
        pandas.errors.EmptyDataError: If the URL does not contain valid CSV data.
        Exception: If another error occurs while fetching or parsing the CSV.
    """
    try:
        df = pd.read_csv(URL)
        logger.info("CSV file read successfully from the web.")
        return df

    except pd.errors.EmptyDataError as e:
        logger.error("The URL does not point to a valid CSV file. Please check the URL and try again.")
        raise

    except Exception as e:
        logger.error(f"Failed to read CSV from the web. Error: {e}")
        raise


# --------------------------------------------------------------------------------
# TESTING MODULE FUNCTIONS (Optional)
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    When this module is executed directly, it performs a basic connectivity
    and data-loading test using parameters from config_params.
    """
    try:
        field_df = query_data(
            create_db_engine(config_params['db_path']),
            config_params['sql_query']
        )

        weather_df = read_from_web_CSV(config_params['weather_csv_path'])
        weather_mapping_df = read_from_web_CSV(config_params['weather_mapping_csv'])

        field_test = field_df.shape
        weather_test = weather_df.shape
        weather_mapping_test = weather_mapping_df.shape

        print(f"field_df: {field_test}, weather_df: {weather_test}, weather_mapping_df: {weather_mapping_test}")

    except Exception as e:
        logger.error(f"Testing failed. Error: {e}")
