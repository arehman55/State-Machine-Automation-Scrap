"""
Configuration and static test data module for OrangeHRM Automation.
Uses 100% built-in Python libraries to maintain fast build speeds and
zero external dependencies.
"""

import json
import os
from pathlib import Path

from src.security import decrypt_password_with_hashlib

# Base directories
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


# ENVIRONMENT & CONFIGURATION LOADING
# 1. Load local .env file manually (Zero external dependencies approach)

env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comments, extract key-value pairs
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# 2. Load local config.json file if it exists
config_path = PROJECT_ROOT / "config.json"
config_data = {}
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

# Point the Robot Framework file and development data to their correct locations
ROBOT_FILE = BASE_DIR / "tasks.robot"
DEVDATA_DIR = BASE_DIR / "devdata"

# Keep generated files alongside the project configuration
OUTPUT_DIR = BASE_DIR / "output"

# Portal Credentials & URLs
BASE_URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
USERNAME = os.getenv("ORANGEHRM_USER", "Admin")


# SECURE PASSWORD HANDLING ( hashlib + secret key)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "CRITICAL: SECRET_KEY is not set in environment or .env file! "
        "Required for decrypting passwords."
    )

# Priority: config.json (encrypted) -> System Environment Variable -> Plaintext fallback
encrypted_password = config_data.get("ORANGEHRM_PASSWORD_ENCRYPTED")

if encrypted_password:
    # Decrypt password securely at runtime for Selenium login
    ORANGEHRM_PASSWORD = decrypt_password_with_hashlib(encrypted_password, SECRET_KEY)
else:
    # Fallback in case the password is provided directly via an environment variable
    ORANGEHRM_PASSWORD = os.getenv("ORANGEHRM_PASSWORD")

if not ORANGEHRM_PASSWORD:
    raise ValueError(
        "CRITICAL: ORANGEHRM_PASSWORD is not set! "
        "Please configure 'ORANGEHRM_PASSWORD_ENCRYPTED' in config.json."
    )

# Backward compatibility alias for any modules importing 'PASSWORD'
PASSWORD = ORANGEHRM_PASSWORD

# Excel Output Paths
PRIMARY_EXCEL_PATH = OUTPUT_DIR / "OrangeHRM_Data.xlsx"
ATTACHMENTS_EXCEL_PATH = OUTPUT_DIR / "OrangeHRM_Attachments.xlsx"
SAMPLE_ATTACHMENT_PATH = DEVDATA_DIR / "sample_attachment.pdf"


def validate_environment() -> None:
    """Create required directories and validate configured project fixtures."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_ATTACHMENT_PATH.exists():
        raise FileNotFoundError(
            f"Required attachment fixture not found: {SAMPLE_ATTACHMENT_PATH}"
        )


MY_INFO_SECTIONS = (
    "Personal_Details",
    "Contact_Details",
    "Emergency_Contacts",
    "Dependents",
    "Immigration",
    "Job",
    "Salary",
    "Report_To",
    "Qualifications",
    "Memberships",
)


def format_my_info_section_label(section_name: str, position: int) -> str:
    """Return the numbered display label for a My Info section."""
    display_name = section_name.replace("_", " ").replace("Report To", "Report-to")
    return f"{position}. {display_name}"


# Phase 2: Timesheet Dummy Data
TIMESHEET_DATA = {
    "project_search_hint": "Apache",
    "hours": {
        "Mon": "08:00",
        "Tue": "08:00",
        "Wed": "07:30",
        "Thu": "08:00",
        "Fri": "08:00",
        "Sat": "04:00",
        "Sun": "00:00",
    },
}

# Phase 3: 10 Sections of "My Info" Dummy Data
MY_INFO_SECTIONS_DATA = {
    "Personal_Details": {
        "first_name": "Muhammad",
        "middle_name": "Abdul",
        "last_name": "Rehman",
        "employee_id": "EMP-9042",
        "other_id": "PK-44210",
        "drivers_license": "DL-998877",
        "license_expiry": "2028-12-31",
        "nationality": "Pakistani",
        "marital_status": "Single",
        "dob": "1999-05-15",
    },
    "Contact_Details": {
        "street_1": "142 Tech Boulevard, Johar Town",
        "street_2": "Street 400",
        "city": "Lahore",
        "state": "Punjab",
        "zip_code": "54000",
        "country": "Pakistan",
        "mobile": "+923001234567",
        "work_email": "test@gmail.com",
    },
    "Emergency_Contacts": {
        "name": "AbdulRehman",
        "relationship": "Myself",
        "home_telephone": "04235551234",
        "mobile": "+923219876543",
        "work_telephone": "04235559999",
    },
    "Dependents": {
        "name": "AbdulRehman",
        "relationship": "Child",
        "dob": "2004-08-10",
    },
    "Immigration": {
        "document_type": "Passport",
        "number": "PK9988112",
        "issued_date": "2022-01-10",
        "expiry_date": "2032-01-09",
        "eligible_status": "Verified Citizen",
        "issued_by": "Pakistan",
        "eligible_review_date": "2026-12-01",
        "comments": "Primary international travel document.",
    },
    "Job": {"verification_note": "Job contract verified via RPA audit."},
    "Salary": {"audit_status": "Verified"},
    "Report_To": {"hierarchy_check": "Completed"},
    "Qualifications": {
        "company": "Enterprise Automation Labs",
        "job_title": "Senior RPA Engineer",
        "from_date": "2024-01-01",
        "to_date": "2026-09-01",
        "comment": "Architected Selenium 4 and Sema4.ai automation pipelines.",
    },
    "Memberships": {
        "membership_index": 1,
        "subscription_paid_by": "Company",
        "subscription_amount": "250",
        "currency_index": 1,
        "commence_date": "2025-01-01",
        "renewal_date": "2027-01-01",
    },
}

# ==============================================================================
# PHASE 4: THUNDERBIRD EMAIL AUTOMATION CONFIGURATION
# ==============================================================================
TEAM_LEAD_EMAIL = os.getenv(
    "TEAM_LEAD_EMAIL", "fa22-bcs-260@students.cuisahiwal.edu.pk"
)
AUTOMATION_AUTHOR = os.getenv("AUTOMATION_AUTHOR", "Automation Bot")
EMAIL_1_SUBJECT = "OrangeHRM RPA Report: Weekly Timesheet Automation Summary"

# Standard Windows installation paths for Mozilla Thunderbird
THUNDERBIRD_PATHS = [
    Path(r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe"),
    Path(r"C:\Program Files (x86)\Mozilla Thunderbird\thunderbird.exe"),
]
