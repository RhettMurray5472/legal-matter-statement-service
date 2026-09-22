from datetime import date

from legal_statement.models import Deadline, DeadlineState
from legal_statement.statement_service import decide_follow_up


def test_unfinished_deadline_due_within_seven_days_requires_follow_up() -> None:
    deadline = Deadline(label="File disclosure", due_on=date(2026, 9, 14))

    decision = decide_follow_up(deadline, as_of_date=date(2026, 9, 8))

    assert decision.state is DeadlineState.DUE_SOON
    assert decision.action_required is True


def test_completed_deadline_does_not_require_follow_up() -> None:
    deadline = Deadline(
        label="File disclosure",
        due_on=date(2026, 9, 7),
        completed_on=date(2026, 9, 6),
    )

    decision = decide_follow_up(deadline, as_of_date=date(2026, 9, 8))

    assert decision.state is DeadlineState.COMPLETE
    assert decision.action_required is False
