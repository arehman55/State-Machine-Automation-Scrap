"""
Centralized Entry Point for the OrangeHRM & Thunderbird RPA Automation Package.
Allows initiating the complete end-to-end Robot Framework suite, Pure Python workflow,
or starting from a specific workflow stage via the Finite State Machine orchestrator.
"""

import argparse
import logging
import sys

from robot import run as robot_run

from src import config
from src.exceptions import OrangeHRMBaseException
from src.keywords.orangehrm_keywords import OrangeHRMKeywords
from src.state_machine import run_with_statemachine

logger = logging.getLogger("CentralizedRunner")


def run_robot_suite() -> int:
    """Run the complete automation suite through Robot Framework.

    Returns:
        int: Robot Framework process return code.
    """
    logger.info(
        "Initiating Full RPA Suite via Robot Framework (%s)...", config.ROBOT_FILE.name
    )

    return_code = robot_run(
        str(config.ROBOT_FILE),
        outputdir=str(config.OUTPUT_DIR),
        pythonpath=[str(config.ROBOT_FILE.parent)],
    )
    return int(return_code)


def run_pure_python_workflow(start_stage: str = "full") -> None:
    """Run the automation phases through the Python keyword library and State Machine.

    Args:
        start_stage (str): Stage to begin from ('full', 'timesheets', 'my_info', 'email').

    Returns:
        None.
    """
    rpa = OrangeHRMKeywords()

    def init_and_authenticate() -> None:
        """Initialize WebDriver and complete Phase 1 login as a mandatory prerequisite."""
        rpa.initialize_browser_session()
        rpa.execute_phase_1_authentication()

    stage_callbacks = {
        "auth": init_and_authenticate,
        "timesheets": rpa.execute_phase_2_time_module,
        "my_info": rpa.execute_phase_3_my_info_module,
        "email": rpa.execute_phase_4_email_reporting,
    }

    cleanup_fn = None if start_stage == "email" else rpa.close_browser_safely

    logger.info(
        "Initiating State Machine Pure Python Execution (Start Stage: '%s')...",
        start_stage,
    )
    run_with_statemachine(
        stage_callbacks=stage_callbacks,
        cleanup_callback=cleanup_fn,
        start_stage=start_stage,
    )
    logger.info("Requested workflow stages completed successfully!")


def main() -> None:
    """Parse command-line arguments and start the selected workflow."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="OrangeHRM Enterprise RPA Centralized Runner"
    )
    parser.add_argument(
        "--mode",
        choices=["robot", "python", "email-only"],
        default="robot",
        help=(
            "'robot': Run full suite via tasks.robot (default) | "
            "'python': Run phases directly via Python State Machine | "
            "'email-only': Run only Phase 4 Thunderbird email automation"
        ),
    )
    parser.add_argument(
        "--stage",
        choices=["full", "timesheets", "my_info", "email"],
        default="full",
        help=(
            "Target stage to start from after mandatory login "
            "('full', 'timesheets', 'my_info', 'email'). Automatically uses Python mode."
        ),
    )
    args = parser.parse_args()

    try:
        config.validate_environment()

        if args.mode == "email-only" or args.stage == "email":
            run_pure_python_workflow(start_stage="email")
        elif args.stage != "full" or args.mode == "python":
            run_pure_python_workflow(start_stage=args.stage)
        else:

            def execute_robot() -> None:
                exit_code = run_robot_suite()
                if exit_code != 0:
                    raise RuntimeError(
                        f"Robot Framework suite exited with code {exit_code}"
                    )

            run_with_statemachine(main_function=execute_robot)

    except (OSError, RuntimeError, ValueError, OrangeHRMBaseException) as exc:
        print(f"Execution failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
