import yaml
import datetime as dt
import inspect
import os


# Pull Config Info from YAML
def prepare_tasks(config_dir: str = "./config.yaml") -> dict:
    """
    Loads task configurations from a YAML file and appends standardized UTC timestamps to each task.

    Args:
        config_dir (str): Path to the YAML configuration file. Defaults to './config.yaml'.

    Returns:
        dict: A dictionary containing two keys:
            - "data": A list of task dictionaries with an added "TIMESTAMPS" field for each.
            - "result": Metadata about the execution including:
                - "task_name": Name of this function
                - "status_message": 'Success' or error message
                - "status_code": 200 for success, 500 for failure

    Timestamp Format Keys Added to Each Task:
        - "_IN_DATA_TIMESTAMP": Human-readable UTC datetime (e.g. '2025-07-30 20:45:00')
        - "_OUT_DATA_TIMESTAMP": File-safe UTC timestamp (e.g. '2025_07_30_204500')
        - "_YEAR_DATA_TIMESTAMP": Year (e.g. '2025')
        - "_MONTH_DATA_TIMESTAMP": Zero-padded month (e.g. '07')
        - "_DAY_DATA_TIMESTAMP": Zero-padded day (e.g. '30')

    Raises:
        Will exit the program if the YAML file cannot be loaded properly.
        Returns a failure `result` block in case of unexpected errors.
    """

    try:
        stamped_tasks = []

        try:
            with open(config_dir, "r") as stream:
                yaml_config = yaml.safe_load(stream)
        except Exception as e:
            print(e)
            print(os.getcwd())
            exit(1)

        TASKS = yaml_config["TASKS"]

        utc_now = dt.datetime.now(dt.timezone.utc)  # datetime for cataloging

        data_timestamps = {

            "_IN_DATA_TIMESTAMP": utc_now.strftime('%Y-%m-%d %H:%M:%S'),  # timestamp found inside data
            "_OUT_DATA_TIMESTAMP": utc_now.strftime('%Y_%m_%d_%H%M%S'),  # timestamp found in file
            "_YEAR_DATA_TIMESTAMP": f'{utc_now.year}',  # folder and path dates
            "_MONTH_DATA_TIMESTAMP": f'{utc_now.month:02d}',  # folder and path dates
            "_DAY_DATA_TIMESTAMP": f'{utc_now.day:02d}',  # folder and path dates

        }

        for TASK in TASKS:
            updated_task = TASK.copy()
            updated_task["TIMESTAMPS"] = data_timestamps
            stamped_tasks.append(updated_task)

        result = {
            "data": stamped_tasks,
            "result": {
                "task_name": inspect.currentframe().f_code.co_name,
                "status_message": "Success",
                "status_code": 200
            }
        }

        return result

    except Exception as e:
        result = {
            "result": {
                "task_name": inspect.currentframe().f_code.co_name,
                "status_message": str(e),
                "status_code": 500
            }
        }

        return result
