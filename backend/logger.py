# logger.py
import csv
import os
from datetime import datetime

LOG_FILE = "interaction_log.csv"


def log_interaction(user_input, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "user_input", "response"])
        writer.writerow([timestamp, user_input, response])
