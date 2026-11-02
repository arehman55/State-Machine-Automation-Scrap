# Enterprise RPA Automation Suite: OrangeHRM and Thunderbird

An end-to-end Robotic Process Automation (RPA) suite built with Python, Robot
Framework, Selenium, and RPA.Desktop. The application automates OrangeHRM
data collection, native Excel encryption, report generation, and desktop email
dispatch through Mozilla Thunderbird.

## Automation Workflow

The suite executes the following four phases:

1. **Secure authentication**
   Logs in to the OrangeHRM portal using Selenium.
2. **Timesheet data extraction**
   Navigates to the Time module, collects employee timesheet records, and
   prepares the data for reporting.
3. **Employee data and Excel generation**
   Extracts information from ten My Info sections and generates formatted Excel
   workbooks. The workbooks are protected with native Office AES encryption
   using `msoffcrypto`.
4. **Desktop email automation**
   Controls Mozilla Thunderbird using CLI compose commands, native window
   locators, and keyboard shortcuts. The timesheet report is sent as an HTML
   email, followed by a threaded reply containing the encrypted workbook and
   password instructions.

## Prerequisites

Install and configure the following before running the suite:

1. Python 3.9 or later.
2. Mozilla Thunderbird with the sender's email account configured.
3. Google Chrome for Selenium-based web automation.
4. Windows 10 or later, or a supported Ubuntu/Linux desktop environment.

The project also requires valid OrangeHRM credentials and the required secret
key configuration. See `config.json` and the environment variables used by
`src/config.py`.

## Installation

The project follows the PEP 621 packaging standard and can be installed from
source or from a built wheel.

### Install From Source

```bash
python -m venv rpa-env

# Linux and macOS
source rpa-env/bin/activate

# Windows PowerShell
# .\rpa-env\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install .
```

### Install From a Wheel

```bash
python -m pip install dist/orangehrm_rpa_automation-1.0.0-py3-none-any.whl
```

## Running the Automation

Installation registers the `run-rpa` command, which can be called from the
project directory or another working directory.

### Run the Complete Suite with Python

```bash
run-rpa --mode python
```

### Run with Robot Framework

```bash
run-rpa --mode robot
```

### Run Email Dispatch Only

```bash
run-rpa --mode email-only
```

## Architecture and Security

- **Page Object Model:** Selenium locators are centralized in
  `src/pages/locators.py` to keep browser interactions maintainable.
- **Native workbook protection:** `msoffcrypto` encrypts generated `.xlsx`
  files using a native Office encryption container. The resulting files can be
  opened in Microsoft Excel and compatible mobile viewers with the password.
- **Cross-platform window control:** Linux uses X11 window handling, while
  Windows uses native Win32 APIs. RPA.Desktop provides keyboard control for
  the final dispatch action.
- **Environment isolation:** Thunderbird is launched with conflicting Conda,
  Snap, GTK, and Wayland environment variables removed where required.

## Testing

Run the unit tests without launching a browser or Thunderbird:

```bash
python -m pytest
```

## Building a Release

The build script removes stale build artifacts and creates a fresh wheel in the
`dist/` directory:

```bash
python build_script.py
```

## Generated Output

Successful execution creates an `output/` directory containing:

- `OrangeHRM_Data.xlsx`: source timesheet workbook.
- `OrangeHRM_Data_protected.xlsx`: natively password-protected timesheet
  workbook attached to the primary email.
- `Details.xlsx`: source employee details workbook.
- `Details_protected.xlsx`: natively password-protected details workbook
  attached to the threaded reply.
- Temporary HTML files used as Thunderbird email bodies.