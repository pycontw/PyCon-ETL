#!/usr/bin/env python3
import argparse
import re

import pandas as pd
from google.cloud import bigquery


def upload_dataframe_to_bigquery(df, project_id, dataset_name, table_name):
    client = bigquery.Client(project=project_id)

    dataset_ref = bigquery.dataset.DatasetReference(project_id, dataset_name)
    table_ref = bigquery.table.TableReference(dataset_ref, table_name)

    # dump the csv into bigquery
    job = client.load_table_from_dataframe(df, table_ref)

    job.result()

    print(
        "Loaded {} rows into {}:{}.".format(job.output_rows, dataset_name, table_name)
    )


def sanitize_column_name(column_name):
    regex = re.compile("[^a-zA-Z]")
    return regex.sub("", column_name)


def sanitize_column_names(df):
    sanitized_columns = {}
    for column in df.columns:
        sanitized_column = sanitize_column_name(column)
        sanitized_columns[column] = sanitized_column

    return df.rename(columns=sanitized_columns)


def main():
    """
    Commandline entrypoint
    """
    parser = argparse.ArgumentParser(
        description="Sanitize ticket CSV and upload to BigQuery"
    )

    parser.add_argument(
        "csv_file", type=str, help="Ticket CSV file",
    )

    parser.add_argument("-p", "--project-id", help="BigQuery project ID")

    parser.add_argument(
        "-d", "--dataset-name", help="BigQuery dataset name to create or append"
    )

    parser.add_argument(
        "-t", "--table-name", help="BigQuery table name to create or append"
    )

    args = parser.parse_args()

    # load the csv into bigquery
    df = pd.read_csv(args.csv_file)
    sanitized_df = sanitize_column_names(df)
    upload_dataframe_to_bigquery(
        sanitized_df, args.project_id, args.dataset_name, args.table_name
    )


if __name__ == "__main__":
    main()
