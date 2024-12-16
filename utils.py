import time
import argparse
import logging

# Set up basic configuration for logging
logging.basicConfig(
    filename='runtime.log',  # Log file name
    level=logging.INFO,     # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def getlogger():
    return logging

def timeit(f):
    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        #print('%sfunc:%r args:[%r, %r] took: %2.4f sec%s' % (bcolors.WARNING, f.__name__, args, kw, te-ts, bcolors.ENDC))
        logging.info('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te-ts))
        return result

    return timed


def parse_args(*args, **kwargs):
    """
    Parse input params
    Returns
    -------
    args: parsed arguments
    """
    parser = argparse.ArgumentParser(description='Pipeline of constructing log template recovery benchmark', *args, **kwargs)
    parser.add_argument(
                        '-l',
                        '--logname',
                        type=str,
                        default=None,
                        help="""
                        Please input the name of the log (e.g., Apache): 
                        """,
                        required=True)
    parser.add_argument('-s',
                        '--stage',
                        type=str,
                        choices=['extract', 'parse', 'match'],
                        required=True,
                        help='Choose the current stage of the pipeline.\n\
                            \t - extract: Extract log content (log message) from raw logs.\n\
                            \t - parse: parsing log content with multiple parsers.\n\
                            \t - match: [AFTER REFINE] Match logs with refined templates')
    parser.add_argument(
                        '-i',
                        '--iteration',
                        type=int,
                        required=True,
                        help="""
                        Specify the number of current iteration; start with 1; 
                        """)
    return parser.parse_known_args()