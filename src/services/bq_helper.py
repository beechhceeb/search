import functools
import time
import warnings
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
import logging
import pandas as pd
from google.api_core.exceptions import DeadlineExceeded
from google.cloud import bigquery
from google.cloud.bigquery import QueryJob
log = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


def make_schema(job: QueryJob) -> pd.DataFrame:
    df = job.to_dataframe()
    schema = job.result().schema
    data_dict = {
        "columns": df.columns.tolist(),
        "example_values": (df.iloc[0].tolist() if not df.empty else []),
        "types": [s.field_type for s in schema],
    }

    return pd.DataFrame(data_dict)


def time_summary(query_job: QueryJob) -> str:
    # Initialize elapsed time
    elapsed_sec = 0.0

    # Utilize the timeline to calculate elapsed time
    if query_job.timeline:
        latest_event = query_job.timeline[-1]
        elapsed_sec = latest_event.elapsed_ms / 1000  # Convert ms to seconds
    else:
        log.debug(
            "Query job does not have a timeline. Elapsed time set to 0 seconds."
        )

    # Access data processed and billed, handling None values
    total_bytes_processed = query_job.total_bytes_processed or 0
    total_bytes_billed = query_job.total_bytes_billed or 0

    # Convert bytes to gigabytes (GB)
    processed_gb = total_bytes_processed / 1_073_741_824  # 1 GB = 1,073,741,824 bytes
    billed_gb = total_bytes_billed / 1_073_741_824

    # Format each component of the summary
    duration_str = f"Duration: {elapsed_sec:.2f} seconds"
    processed_str = f"Data Processed: {processed_gb:.2f} GB"
    billed_str = f"Data Billed: {billed_gb:.2f} GB"

    # Combine all parts into the final summary
    return f"{duration_str}\n\t{processed_str}\n\t{billed_str}"


def make_custom_error_message(e, job):
    location = job.location or "US"
    project_id = job.project
    job_id = job.job_id
    bq_link = (
        "https://console.cloud.google.com/bigquery"
        "?referrer=search"
        "&inv=1"
        "&invt=AboO5g"
        f"&project={project_id}"
        f"&ws=!1m5!1m4!1m3!1s{project_id}!2s{job_id}!3s{location}"
    )
    error_str = str(e)
    short_msg = error_str.split("400 ", 1)[-1]  # everything after "400 "
    parts = short_msg.split(": ", 2)  # Remove inaccessible link in error message
    cleaned_message = parts[0] + ": " + parts[-1]
    msg = f"Query failed: {cleaned_message}\nInspect it here:\n{bq_link}\n\n\n\n\n"
    return msg


def handle_silent(method: Callable) -> Callable:
    """
    Handle the 'silent' parameter for public methods.

    If silent=True, suppresses all outputs.
    """

    @functools.wraps(method)
    def wrapper(self: any, *args: list, **kwargs: dict) -> Callable[..., Any] | None:
        silent = kwargs.pop("silent", False)
        if silent:
            log.disable("dsci_utilities.BQHelper")
            try:
                return method(self, *args, **kwargs)
            finally:
                log.enable("dsci_utilities.BQHelper")
        else:
            return method(self, *args, **kwargs)

    return wrapper


class BQHelper:
    """
    Provides utility tools to run sql queries stored in text file against Big Query from Python.

    Be sure to update scratch area for location of saved tables to your personal area.
    Expects sql to be stored in a text file in the folder specified below.
    """

    def __init__(
        self,
        billing_project_id: str,
        write_project_id: str,
        read_project_id: str,
        write_dataset: str,
        read_dataset: str,
        daw_dataset: str,
        sql_folder: str,
        logging_folder: str | None = None,
        validate: bool = False,
        timeout: int = 3600,
        client: bigquery.Client | None = None,
    ) -> None:
        """
        Initialize the Helper instance.

        This constructor sets up the necessary parameters for the Helper class,
        including project details, dataset information, and paths for SQL and logging.

        Args:
            billing_project_id (str): The project ID to be billed for the BigQuery operations.
            write_project_id (str): The project ID where the tables will be written.
            read_project_id (str): The project ID where the tables will be read.
            write_dataset (str): The dataset where the tables will be written.
            read_dataset (str): The dataset where the tables will be read.
            daw_dataset (str): The dataset where the tables will be read.
            sql_folder (str): The folder containing the SQL scripts.
            logging_folder (str): The folder where the SQL logs will be saved.
            validate (bool): If True, enables validation mode for the Helper instance.
            timeout (int): The timeout duration for BigQuery operations in seconds.
            client (bigquery.Client): Optional BigQuery client. If not provided, a new client will be created.

        """
        self.billing_project_id = billing_project_id
        self.write_project_id = write_project_id
        self.read_project_id = read_project_id
        self.write_dataset = write_dataset
        self.read_dataset = read_dataset
        self.daw_dataset = daw_dataset
        self.sql_folder = sql_folder
        self.sql_log_folder = logging_folder
        self.validate = validate
        self.timeout = timeout
        self.client = client or bigquery.Client(project=self.billing_project_id)

    def _read_sql(self, script: str) -> str:
        sql_path = Path(self.sql_folder) / f"{script}.sql"
        with sql_path.open() as f:
            return f.read()

    def _make_full_table(
        self,
        table: str,
        write_project_id: str | None = None,
        write_dataset: str | None = None,
        *,
        backtick: bool = True,
    ) -> str:
        """
        This makes a string for when we are using a creation table statement with the placeholder 'table'.
        Since its always for a creation statement we use the write_project and write_dataset
        """
        write_project_id = write_project_id or self.write_project_id
        write_dataset = write_dataset or self.write_dataset
        table = f"{write_project_id}.{write_dataset}.{table}"
        if backtick:
            return f"`{table}`"
        return table

    def _validate_query(self, df, sql):
        log.info("Dry run mode: validating SQL without execution")
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = self.client.query(sql, job_config=job_config)
        # Wait for dry run validation
        job.result()
        log.info(f"Query is valid. Estimated to process {job.total_bytes_processed / 1e9:.2f} GB.")
        return df  # Return empty df in dry run

    def _run_query(
        self, sql: str, *, return_df: bool = False, return_schema: bool = False
    ) -> pd.DataFrame:
        df = pd.DataFrame()  # Return empty df if return_df=False

        if self.validate:
            return self._validate_query(df, sql)

        job = self.client.query(sql)

        try:
            job.result(timeout=self.timeout)
            summary = time_summary(job)

            if return_df:
                df = job.to_dataframe()
                summary = (
                    summary + f"\nReturned {df.shape[0]} rows, {df.shape[1]} columns"
                )

            if return_schema:
                df = make_schema(job)

            log.info("\n\t" + summary + "\n")

        except DeadlineExceeded:
            job.cancel()
            log.exception("Timeout limit reached!")
            raise
        except Exception as e:
            msg = make_custom_error_message(e, job)
            log.error(msg)
            raise
        else:
            return df

    def _write(self, df: pd.DataFrame, table: str) -> None:
        if self.validate:
            log.info(f"[VALIDATION MODE] Would write to table `{table}` ({len(df)} rows)")
            return

        try:
            job = self.client.load_table_from_dataframe(
                df, table, job_config=bigquery.LoadJobConfig()
            )
            job.result()

            table = self.client.get_table(table)
            loaded_summary = f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table}"

            log.info(loaded_summary)

        except Exception:
            log.exception("Error executing query")
            raise

    def _log_file(self, text: str, query_name: str) -> None:
        Path(self.sql_log_folder).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{self.sql_log_folder}/{query_name}_{timestamp}.sql"

        with Path(path).open("w", encoding="utf-8") as f:
            f.write(str(text))

    def _prepare_sql(self, script: str, **kwargs: Any) -> str:
        """
        Read and format an SQL script with provided parameters.
        Also logs the SQL if a log folder is configured.
        """
        sql = self._read_sql(script)
        table = self._make_full_table(table=script)
        sql = sql.format(
            table=table,
            write_project=kwargs.get("write_project_id", self.write_project_id),
            read_project=kwargs.get("read_project_id", self.read_project_id),
            write_dataset=kwargs.get("write_dataset", self.write_dataset),
            read_dataset=kwargs.get("read_dataset", self.read_dataset),
            daw_dataset=kwargs.get("daw_dataset", self.daw_dataset),
            **kwargs,
        )

        log.info(f"Running script: {script}")

        if self.sql_log_folder:
            self._log_file(text=sql, query_name=table)

        return sql

    @handle_silent
    def run(self, script: str, **kwargs: Any) -> None:
        """
        Execute an SQL script located in the SQL queries folder.

        Args:
            script (str): Name of the SQL script file (without .sql extension) located in the sql_folder.
            **kwargs: Additional parameters to interpolate into the SQL script. For example, start_date=start_date.

        """
        sql = self._prepare_sql(script=script, **kwargs)
        self._run_query(sql=sql)

    @handle_silent
    def get(self, script: str, **kwargs: Any) -> pd.DataFrame:
        """
        Execute an SQL script located in the SQL queries folder. Returns df.

        Keyword Arguments:
            script: provide the name of the script in sql queries folder to open.
            **kwargs: enter the parameter names that are contained in your script. e.g. start_date = start_date.

        """
        sql = self._prepare_sql(script=script, **kwargs)
        return self._run_query(sql=sql, return_df=True)

    @handle_silent
    def run_string(self, string: str) -> None:
        """
        Execute a raw SQL query string against BigQuery.

        Args:
            string (str): The SQL query to be executed.

        """
        log.info(f"Running string: {string}")

        self._run_query(sql=string)

    @handle_silent
    def get_string(self, string: str) -> pd.DataFrame:
        """
        Execute a raw SQL query string against BigQuery. Returns df.

        Args:
            string (str): The SQL query to be executed.

        """
        log.info(f"Running string: {string}")

        return self._run_query(sql=string, return_df=True)

    @handle_silent
    def write_to(self, df: pd.DataFrame, table: str, *, replace: bool = True) -> None:
        """
        Use credentials provided above to write a supplied dataframe to a supplied table name in the scratch area above.

        Args:
            df: dataframe object to write
            table: string of table name to write to
            replace (bool, optional): If True, replace any existing table. Defaults to True

        """
        table = self._make_full_table(table=table, backtick=False)

        log.info(f"Writing df to table: `{table}`")

        if replace:
            sql = f"DROP TABLE IF EXISTS `{table}`"
            self._run_query(sql=sql)
            time.sleep(1)  # Rate limit error without sleep

        self._write(df=df, table=table)

    @handle_silent
    def get_table(
        self, table: str, project_id: str | None = None, dataset: str | None = None
    ) -> pd.DataFrame:
        """
        Retrieve all rows from a specified BigQuery table.

        Args:
            table (str): The name of the BigQuery table to select data from.
            project_id (str, optional): The ID of the project containing the table.
            dataset (str, optional): The ID of the dataset containing the table.

        """
        table = self._make_full_table(
            table=table, write_project_id=project_id, write_dataset=dataset
        )
        sql = f"select * from {table}"  # NOQA: S608

        log.info("Getting table: " + table)

        if self.sql_log_folder:
            self._log_file(text=sql, query_name=table)

        return self._run_query(sql=sql, return_df=True)

    @handle_silent
    def get_table_data_dict(self, table: str) -> pd.DataFrame:
        """
        Return the data dict for a table. 1st row of data included.

        Args:
            table: FULL x.x.x name of BQ table to return schema and example row for

        """
        sql = "select * from `{table}` limit 1"
        sql = sql.format(table=table)

        log.info(f"Creating data dict of: {table}")

        return self._run_query(sql=sql, return_schema=True)