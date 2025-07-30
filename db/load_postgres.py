########################################################
#
#     Title: Postgres [LOAD]
#     Created by: Gabe McWilliams
#     Date: 2023/04/19
#
########################################################


import os
from sqlalchemy import create_engine
import hvac
import traceback
import inspect


class PostgresLoad:

    def __init__(self, df_input, config: dict, vault) -> None:
        self.__df_input = df_input
        self.__details = config["DETAILS"]
        self.__data = config["DATA"]
        self.__timestamps = config["TIMESTAMPS"]
        self.__secrets = config["SECRETS"]
        self.__secrets.update(
            vault.read_secret(
                mount_point=config["SECRETS"]["mount_point"],
                path=config["SECRETS"]["path"]
            )
        )

    def load_to_postgres(self):
        print(f'\n============  [START] - {inspect.currentframe().f_code.co_name}  ============\n')

        database = self.__data["destination"]["database"]
        schema = self.__data["destination"]["schema"]
        table = f'{self.__data["source_method"]}_{self.__data["destination"]["table"]}'

        try:
            # GET THE POSTGRES SECRETS AND BUILD THE DB URI
            user = self.__secrets["POSTGRES_USER"]
            password = self.__secrets["POSTGRES_PASSWORD"]
            uri = self.__secrets["POSTGRES_URI"]
            port = self.__secrets["POSTGRES_PORT"]

            # DEFINE THE DB URI
            db_uri = f'postgresql://{user}:{password}@{uri}:{port}/{database}'

            # DEFINE THE ENGINE (CONNECTION OBJECT)
            engine = create_engine(db_uri, echo=True)

            self.__df_input.to_sql(table, con=engine, if_exists='replace', index=False, schema=schema)

            return {
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 200,
                    "database": database,
                    "schema": schema,
                    "table": table,
                    "content-type": "application/json",
                    "message": "Data loaded successfully",
                }
            }

        except Exception as e:
            t = traceback.format_exc()
            return {
                "result": {
                    "job_title": self.__details["task_title"],
                    "status_code": 500,
                    "database": database,
                    "schema": schema,
                    "table": table,
                    "message": t,
                }
            }
