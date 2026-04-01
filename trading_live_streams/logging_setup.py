import logging
from pathlib import Path
from datetime import datetime

# setup logging instance once for the entire project

def init_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok= True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_file = log_dir/f"app_{timestamp}.log"


    logging.basicConfig(
        level=logging.INFO,  # minimum logging level is set to level 20 INFO
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  #log message format
        handlers =[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)
