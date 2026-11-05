# Enterprise RPA Automation Suite: OrangeHRM and Thunderbird

An end-to-end Robotic Process Automation (RPA) suite built with Python, Robot Framework, Selenium, RPA.Desktop, and `python-statemachine`. The application automates OrangeHRM data collection, native Excel encryption, report generation, and desktop email dispatch through Mozilla Thunderbird under strict Finite State Machine orchestration.

## Automation Workflow

The suite executes the following four phases:

1. **Secure authentication**
   Logs in to the OrangeHRM portal using Selenium WebDriver with explicit waits.

2. **Timesheet data extraction**
   Navigates to the Time module, inputs daily timesheet allocations, collects employee records, and prepares data for export.

3. **Employee data and Excel generation**
   Traverses ten My Info sections, manages attachments, and generates formatted Excel workbooks protected with native Office AES encryption via `msoffcrypto`.

4. **Desktop email automation**
   Controls Mozilla Thunderbird using CLI compose commands, native window locators, and keyboard shortcuts to dispatch reports and encrypted workbooks.

## State Machine Orchestration

The pipeline is governed by `OrangeHRMStateMachine` (`src/state_machine.py`), providing fault tolerance, explicit state transitions, and dynamic stage routing:

* **State Hierarchy:**
  `idle` -> `authenticating` -> `processing_timesheets` -> `processing_my_info` -> `dispatching_report` -> `completed` (or `failed` upon unhandled exceptions).

* **Prerequisite Authentication Enforcement:**
  Selecting downstream web stages (such as `my_info` or `timesheets`) guarantees that browser initialization and portal login run first before routing to the target stage.

* **Automated Lifecycle Teardown:**
  Safe browser resource cleanup is bound to both `completed` and `failed` state entry callbacks.

## Prerequisites

Install and configure the following before running the suite:

1. Python 3.9 or later.

2. Mozilla Thunderbird with the sender email account configured.

3. Google Chrome and compatible ChromeDriver for Selenium automation.

4. Windows 10/11 or Ubuntu/Linux desktop environment (X11 supported).

Configure credentials and secrets via environment variables or `src/config.py`.

## Installation

The project follows the PEP 621 packaging standard and can be installed from source or a prebuilt wheel.

### Install From Source

```
python -m venv orangehrm-env

# Linux and macOS
source orangehrm-env/bin/activate

# Windows PowerShell
# .\orangehrm-env\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e .

```

### Install From a Wheel

```
python -m pip install dist/orangehrm_rpa_automation-1.0.0-py3-none-any.whl

```

## Running the Automation

Execute the suite directly via the registered CLI runner or Python module commands.

### Complete Suite via Robot Framework (Default)

```
python -m src.cli
# or
run-rpa --mode robot

```

### Complete Suite via Pure Python State Machine

```
python -m src.cli --mode python
# or
run-rpa --mode python

```

### Dynamic Stage Execution via State Machine

The state machine allows targeting specific phases while enforcing prerequisite authentication:

* **Start directly from My Info (bypasses Timesheets after login):**

  ```
  python -m src.cli --stage my_info
  
  ```

* **Start directly from Timesheets:**

  ```
  python -m src.cli --stage timesheets
  
  ```

* **Run Phase 4 Email Reporting Only (bypasses browser):**

  ```
  python -m src.cli --stage email
  # or
  run-rpa --mode email-only
  
  ```

## Architecture and Security

* **Finite State Machine:** Built using `python-statemachine` with custom transition guards (`is_logged_in`, `should_skip_to_my_info`) to decouple orchestration from execution logic.

* **Page Object Model:** Centralizes element definitions in `src/pages/locators.py` to keep UI interactions decoupled and resilient.

* **Native Workbook Protection:** `msoffcrypto` encrypts generated `.xlsx` workbooks using standard Office AES encryption containers.

* **Cross-Platform Window Control:** Linux uses X11 window handling, while Windows uses Win32 APIs. RPA.Desktop handles keyboard events for final Thunderbird dispatches.

* **Environment Isolation:** Thunderbird is launched with sanitized environment variables (stripping conflicting GTK, Snap, and Wayland configurations on Linux).

## Testing

Run unit tests and verification checks without launching external desktop processes:

```
python -m pytest

```

## Building a Release

Generate fresh package wheels and source distributions:

```
python build_script.py

```

## Generated Output

Successful execution creates an `output/` directory containing:

* `OrangeHRM_Data.xlsx`: Raw extracted timesheet data workbook.

* `OrangeHRM_Data_protected.xlsx`: Password-protected timesheet workbook attached to the primary email.

* `Details.xlsx`: Raw extracted employee details workbook.

* `Details_protected.xlsx`: Password-protected details workbook attached to the follow-up email.

* Diagnostic logs and error screenshots (e.g., `phase3_my_info_failure.png` generated upon UI timeouts).