import logging

class Logger(object):

    def __init__(self):
        # Opens the log file
        root_logger= logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logger.log', 'a', 'utf-8')
        root_logger.addHandler(handler)
    
    def log(self, origin, type, message):
        log_message = f'{origin}: {message}'

        print(log_message)

        if(type == "debug"):
            logging.debug(log_message)
        elif(type == "info"):
            logging.info(log_message)
        elif(type == "warning"):
            logging.warning(log_message)
        elif(type == "error"):
            logging.error(log_message)
    