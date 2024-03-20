import os

from dotenv import load_dotenv

load_dotenv()

ABUSEIPDB_KEY = os.getenv("LOGLYZER_ABUSEIPDB_KEY")
DATETIME_FORMAT = os.getenv("LOGLYZER_DATETIME_FORMAT")
DOMAIN = os.getenv("LOGLYZER_DOMAIN")
FILENAME_REGEX = os.getenv("LOGLYZER_FILENAME_REGEX")
LINE_REGEX = os.getenv("LOGLYZER_LINE_REGEX")
PATH = os.getenv("LOGLYZER_PATH")
