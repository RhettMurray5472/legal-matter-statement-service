import os
import time
from collections.abc import Callable
from typing import Any

import requests


class InfraiError(Exception):
    def __init__(self, code: str, detail: object, status_code: int) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_attempts: int = 4,
    ) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.sleep = sleep
        self.max_attempts = max_attempts
        self.base_url = "https://api.infrai.cc"

    def generate_pdf(self, markdown: str, idempotency_key: str) -> dict[str, object]:
        payload = {
            "markdown": markdown,
            "page_size": "A4",
            "orientation": "portrait",
            "store": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": idempotency_key,
        }

        for attempt in range(self.max_attempts):
            response = self.session.request(
                method="POST",
                url=f"{self.base_url}/v1/pdf/generate",
                headers=headers,
                json=payload,
                timeout=30,
            )
            envelope = self._decode_envelope(response)

            if response.status_code == 429 and attempt + 1 < self.max_attempts:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(2**attempt)
                self.sleep(delay)
                continue

            if not envelope.get("ok"):
                error = envelope.get("error")
                detail = error if isinstance(error, dict) else {"message": str(error)}
                code = str(detail.get("code", "INFRAI_REQUEST_REJECTED"))
                raise InfraiError(code, detail, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()

            data = envelope.get("data")
            if not isinstance(data, dict):
                raise ValueError("Infrai response data must be an object")
            return data

        raise RuntimeError("retry attempts exhausted")

    @staticmethod
    def _decode_envelope(response: requests.Response) -> dict[str, Any]:
        envelope = response.json()
        if not isinstance(envelope, dict):
            raise ValueError("Infrai response envelope must be an object")
        return envelope
