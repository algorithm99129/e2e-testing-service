import logging
from utils.db import log_test_message


class SQLiteHandler(logging.Handler):
    def __init__(self, test_id):
        logging.Handler.__init__(self)
        self.test_id = test_id

    def emit(self, record):
        log_entry = self.format(record)
        message_type = "info" if record.levelno <= logging.INFO else "error"
        log_test_message(self.test_id, log_entry, message_type)
