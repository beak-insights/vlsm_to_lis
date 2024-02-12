import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = "hl7"
DB_USER = "interface"
DB_PASSWORD = "Nmrl123456$"
DB_HOST = "192.168.1.8:3306"

SENAITE_HOST = "192.168.0.32:80"
SENAITE_BASE_URL = f"http://{SENAITE_HOST}/senaite/@@API/senaite/v1/"
SENAITE_USER = "system_daemon"
SENAITE_PASSWORD = "s89Ajs-UIas!3k"
VERIFY_RESULT = False

SLEEP_SECONDS = 5
SLEEP_SUBMISSION_COUNT = 10
POLL_HL7BD_EVERY = 10

LINUX_USING_CRON_TIME_SCHEDULER = False

EXCLUDE_RESULTS = ["ValueNotSet"]

# Keyword mappings
KEYWORDS_MAPPING = {
    # Abbott
    "HIV1mlDBS": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV1.0mlDBS": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV06ml": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    "HIV0.2ml": ["Abbott", "HIV06ml", "VLDBS", "VLPLASMA", ],
    # Roche Cobas
    "HI2DIL96": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2DIL48": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2CAP48": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    "HI2CAP96": ["HI2CAP96", "VLDBS", "VLPLASMA", ],
    # Roche 6800/8800
    "HIVVL": ["VLPLASMA", "EID"],
    # Hologic Panther
    "qHIV-1": ["ViralLoad", "VLDBS", "VLPLASMA", ],
    "HIV-1": ["ViralLoad", "VLDBS", "VLPLASMA", ],
}

DEBUG_LOGGING = False
