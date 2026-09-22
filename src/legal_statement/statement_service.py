from datetime import timedelta
from decimal import Decimal

from .infrai_client import InfraiClient
from .models import Deadline, DeadlineState, FollowUp, StatementExport, StatementRequest


def decide_follow_up(deadline: Deadline, as_of_date) -> FollowUp:
    if deadline.completed_on is not None:
        return FollowUp(state=DeadlineState.COMPLETE, action_required=False)
    if deadline.due_on < as_of_date:
        return FollowUp(state=DeadlineState.OVERDUE, action_required=True)
    if deadline.due_on <= as_of_date + timedelta(days=7):
        return FollowUp(state=DeadlineState.DUE_SOON, action_required=True)
    return FollowUp(state=DeadlineState.SCHEDULED, action_required=False)


def render_statement(request: StatementRequest, follow_up: FollowUp) -> str:
    total = sum((entry.amount for entry in request.entries), start=Decimal("0"))
    rows = "\n".join(
        f"| {entry.posted_on.isoformat()} | {entry.description} | {entry.amount:.2f} |"
        for entry in request.entries
    )
    delivery = request.signed_delivery
    deadline = request.deadline
    return f"""# Matter account statement

**Matter:** {request.matter.matter_id}  
**Client reference:** {request.matter.client_reference}  
**Practice area:** {request.matter.practice_area}  
**Opened:** {request.matter.opened_on.isoformat()}  
**Statement date:** {request.as_of_date.isoformat()}

## Account activity

| Posted | Description | Amount |
|---|---|---:|
{rows}

**Balance:** {total:.2f}

## Signed document delivery

**Document:** {delivery.document_label}  
**Signed:** {delivery.signed_on.isoformat()}  
**Delivered:** {delivery.delivered_on.isoformat()}

## Deadline follow-up

**Deadline:** {deadline.label}  
**Due:** {deadline.due_on.isoformat()}  
**State:** {follow_up.state.value}  
**Action required:** {"yes" if follow_up.action_required else "no"}
"""


def export_statement(request: StatementRequest, client: InfraiClient) -> StatementExport:
    follow_up = decide_follow_up(request.deadline, request.as_of_date)
    markdown = render_statement(request, follow_up)
    idempotency_key = f"statement:{request.matter.matter_id}:{request.as_of_date.isoformat()}"
    pdf = client.generate_pdf(markdown, idempotency_key)
    return StatementExport(
        matter_id=request.matter.matter_id,
        follow_up=follow_up,
        pdf=pdf,
    )
