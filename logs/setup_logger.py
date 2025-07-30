import logging
import datetime as dt
import os


class Logger:

    def __init__(self, config: dict, vault) -> None:

        print("inside logger")
        # print(task)
        self.logger = logging.getLogger(config["JOB_TITLE"])
        logs_dir = config["LOGS_DIR"] + "/" + config["JOB_TITLE"]
        try:
            os.mkdir(logs_dir)
        except Exception as e:
            pass

        formatter = logging.Formatter(
            "%(asctime)s,%(levelname)s,[%(lineno)d],%(funcName)s(),%(message)s",
            "%Y-%m-%d %H:%M:%S")
        filename = f'{logs_dir}/{config["JOB_TITLE"]}_{dt.datetime.now(dt.timezone.utc).strftime("%Y_%m_%d")}.log'
        fileHandler = logging.FileHandler(filename, mode="a")  # 'a' for append you can use 'w' for write
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f'Starting {config["JOB_TITLE"]}')

    def get_logger(self):
        return self.logger
