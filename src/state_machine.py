"""
Finite State Machine Orchestrator for the OrangeHRM RPA Pipeline.

Enforces authentication as a mandatory prerequisite for web stages (timesheets,
my_info) before dynamically routing execution to the requested starting stage.
"""

from typing import Callable, Dict, Optional

from statemachine import State, StateMachine


class OrangeHRMStateMachine(StateMachine):
    """State machine implementation for the OrangeHRM RPA pipeline."""

    idle = State(initial=True)
    authenticating = State()
    processing_timesheets = State()
    processing_my_info = State()
    dispatching_report = State()
    completed = State(final=True)
    failed = State(final=True)

    # Start transitions: Web stages MUST go through authenticating first; email-only goes straight to report
    start = idle.to(
        authenticating, cond=["is_ready", "requires_browser_auth"]
    ) | idle.to(dispatching_report, cond=["is_ready", "is_email_only_stage"])

    # Dynamic routing after authentication based on the requested start_stage
    advance = (
        authenticating.to(
            processing_timesheets, cond=["is_logged_in", "should_run_timesheets"]
        )
        | authenticating.to(
            processing_my_info, cond=["is_logged_in", "should_skip_to_my_info"]
        )
        | processing_timesheets.to(processing_my_info)
        | processing_my_info.to(dispatching_report)
        | dispatching_report.to(completed)
    )

    # Direct completion when wrapping a monolithic runner (like Robot Framework)
    succeed = (
        authenticating.to(completed)
        | processing_timesheets.to(completed)
        | processing_my_info.to(completed)
        | dispatching_report.to(completed)
    )

    # Safe failure transitions from any active state
    fail = (
        idle.to(failed)
        | authenticating.to(failed)
        | processing_timesheets.to(failed)
        | processing_my_info.to(failed)
        | dispatching_report.to(failed)
    )

    VALID_STAGES = ("full", "timesheets", "my_info", "email")

    def __init__(
        self,
        execution_callback: Optional[Callable] = None,
        stage_callbacks: Optional[Dict[str, Callable]] = None,
        cleanup_callback: Optional[Callable] = None,
        start_stage: str = "full",
    ) -> None:
        """
        Initialize the OrangeHRM state machine orchestrator.

        Args:
            execution_callback (Optional[Callable]): Single function to run full suite.
            stage_callbacks (Optional[Dict[str, Callable]]): Map of phase functions
                ('auth', 'timesheets', 'my_info', 'email').
            cleanup_callback (Optional[Callable]): Teardown function to close browser safely.
            start_stage (str): Target stage to start from ('full', 'timesheets', 'my_info', 'email').
        """
        if start_stage not in self.VALID_STAGES:
            raise ValueError(
                f"Invalid start_stage '{start_stage}'. Must be one of {self.VALID_STAGES}."
            )

        self.execution_callback = execution_callback
        self.stage_callbacks = stage_callbacks or {}
        self.cleanup_callback = cleanup_callback
        self.start_stage = start_stage
        self.logged_in = False
        super().__init__()

    # Guards

    def is_ready(self) -> bool:
        """Check if either a main callback or stage callbacks are provided."""
        return self.execution_callback is not None or bool(self.stage_callbacks)

    def requires_browser_auth(self) -> bool:
        """Check if the selected start_stage requires browser initialization and login."""
        return self.start_stage in ("full", "timesheets", "my_info")

    def is_email_only_stage(self) -> bool:
        """Check if execution should jump directly to Phase 4 email reporting."""
        return self.start_stage == "email"

    def is_logged_in(self) -> bool:
        """Confirm that browser authentication succeeded before entering downstream web stages."""
        return self.logged_in

    def should_run_timesheets(self) -> bool:
        """Route to Phase 2 (Timesheets) when start_stage is 'full' or 'timesheets'."""
        return self.start_stage in ("full", "timesheets")

    def should_skip_to_my_info(self) -> bool:
        """Bypass Phase 2 (Timesheets) and route directly to Phase 3 (My Info)."""
        return self.start_stage == "my_info"

    # State Callbacks

    def on_enter_authenticating(self) -> None:
        """Run mandatory browser initialization and Phase 1 authentication."""
        print(
            f"[FSM] Entering 'authenticating' state (Target stage: '{self.start_stage}')..."
        )
        if "auth" in self.stage_callbacks:
            self.stage_callbacks["auth"]()
            self.logged_in = True
        elif self.execution_callback and not self.stage_callbacks:
            self.execution_callback()
            self.logged_in = True

    def on_enter_processing_timesheets(self) -> None:
        """Run Phase 2: Time -> My Timesheets automation."""
        print("[FSM] Entering 'processing_timesheets' state (Phase 2)...")
        if "timesheets" in self.stage_callbacks:
            self.stage_callbacks["timesheets"]()

    def on_enter_processing_my_info(self) -> None:
        """Run Phase 3: My Info 10 sub-sections automation and scraping."""
        print("[FSM] Entering 'processing_my_info' state (Phase 3)...")
        if "my_info" in self.stage_callbacks:
            self.stage_callbacks["my_info"]()

    def on_enter_dispatching_report(self) -> None:
        """Run Phase 4: Thunderbird desktop email reporting."""
        print("[FSM] Entering 'dispatching_report' state (Phase 4)...")
        if "email" in self.stage_callbacks:
            self.stage_callbacks["email"]()

    def on_enter_completed(self) -> None:
        """Run cleanup callback and log successful workflow completion."""
        if self.cleanup_callback:
            self.cleanup_callback()
        print("[FSM] Workflow executed successfully under state machine supervision.")

    def on_enter_failed(self) -> None:
        """Run cleanup callback and log safe workflow termination on failure."""
        if self.cleanup_callback:
            self.cleanup_callback()
        print("[FSM] Workflow failed and aborted safely.")

    def after_transition(self, event: str, source: State, target: State) -> None:
        """Log every completed state transition."""
        print(f"[FSM Log] Transition '{event}': '{source.id}' -> '{target.id}'")


def run_with_statemachine(
    main_function: Optional[Callable] = None,
    stage_callbacks: Optional[Dict[str, Callable]] = None,
    cleanup_callback: Optional[Callable] = None,
    start_stage: str = "full",
) -> None:
    """
    Execute the OrangeHRM RPA workflow under state machine control.

    Args:
        main_function (Optional[Callable]): Monolithic function to run.
        stage_callbacks (Optional[Dict[str, Callable]]): Phase-specific callbacks.
        cleanup_callback (Optional[Callable]): Browser cleanup callback.
        start_stage (str): Target stage to start from ('full', 'timesheets', 'my_info', 'email').
    """
    machine = OrangeHRMStateMachine(
        execution_callback=main_function,
        stage_callbacks=stage_callbacks,
        cleanup_callback=cleanup_callback,
        start_stage=start_stage,
    )

    try:
        machine.start()

        if main_function is not None and not stage_callbacks:
            machine.succeed()
        else:
            while not (machine.completed.is_active or machine.failed.is_active):
                machine.advance()

    except Exception as error:
        print(f"[FSM Error] Exception caught: {error}")
        if not machine.failed.is_active:
            machine.fail()
        raise
