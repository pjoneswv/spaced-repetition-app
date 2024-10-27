import logging

def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(error_message):
    logging.error(error_message)

def log_info(info_message):
    logging.info(info_message)

