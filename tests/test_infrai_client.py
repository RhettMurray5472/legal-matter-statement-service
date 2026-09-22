from dataclasses import dataclass, field

import pytest

from legal_statement.infrai_client import InfraiClient, InfraiError


@dataclass
class FakeResponse:
    status_code: int
    body: dict[str, object]
    headers: dict[str, str] = field(default_factory=dict)

    def json(self) -> dict[str, object]:
        return self.body

    def raise_for_status(self) -> None:
        raise AssertionError("HTTP status was checked before the business envelope")


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_business_rejection_is_read_from_envelope_before_http_status() -> None:
    session = FakeSession(
        [FakeResponse(400, {"ok": False, "data": None, "error": {"code": "BAD_INPUT"}})]
    )
    client = InfraiClient(api_key="test-key", session=session)

    with pytest.raises(InfraiError) as caught:
        client.generate_pdf("# Statement", "statement:M-1:2026-09-08")

    assert caught.value.code == "BAD_INPUT"
    assert caught.value.status_code == 400


def test_rate_limit_reuses_idempotency_key_and_honours_retry_after() -> None:
    sleeps: list[float] = []
    session = FakeSession(
        [
            FakeResponse(429, {"ok": False, "error": {"code": "RATE_LIMIT"}}, {"Retry-After": "3"}),
            FakeResponse(200, {"ok": True, "data": {"job_id": "job-1"}, "error": None}),
        ]
    )
    client = InfraiClient(api_key="test-key", session=session, sleep=sleeps.append)

    result = client.generate_pdf("# Statement", "statement:M-1:2026-09-08")

    assert result == {"job_id": "job-1"}
    assert sleeps == [3.0]
    assert session.calls[0]["headers"] == session.calls[1]["headers"]
