from colorama import Fore, Style
import logging
import sys
import os
class Logger(object):

    def __init__(self):
        root_logger = logging.getLogger()

        if not root_logger.hasHandlers():
            
            root_logger.setLevel(logging.WARNING) # Replace this for INFO to hide debug messages from logger
            
            handler = logging.FileHandler('logger.log', 'a', 'utf-8')
            root_logger.addHandler(handler)
            
            ### Add success as a level
            try:
                addLoggingLevel('SUCCESS', logging.INFO)
            except AttributeError:
                pass
        
    
    def log(self, origin : str, type_message : str, message : str) -> None:

        ### Falta dar add a um logging level para o success (se ainda quiseres usar isso, senão usamos o default)
        ### Tem código para como fazer isso em baixo da classe

        msg = f'{origin}: {message}'
        
        if (type_message == "info"):
            print(f"{Fore.CYAN}[ INFO ] {msg} {Style.RESET_ALL}")
            logging.info(f"[ INFO ] {msg}")
        elif (type_message == "warning"):
            print(f"{Fore.YELLOW}[ WARN ] {msg} {Style.RESET_ALL}")
            logging.warning(f"[ WARN ] {msg} ")
        elif (type_message == "error"):
            print(f"{Fore.RED}[ ERROR ] {msg} {Style.RESET_ALL}")
            logging.error(f"[ ERROR ] {msg} ")
        elif (type_message == "success"):
            print(f"{Fore.GREEN}[ SUCCESS ] {msg} {Style.RESET_ALL}")
            logging.success(f"[ SUCCESS ] {msg} ")
        elif (type_message == "debug"):
            # print(f"{Fore.MAGENTA}[ DEBUG ] {msg} {Style.RESET_ALL}")
            logging.debug(f"[ DEBUG ] {msg} ")
        

### Link: https://stackoverflow.com/a/35804945/1691778
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)