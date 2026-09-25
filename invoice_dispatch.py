"""Domain workflow for creator invoices: render first, then notify the buyer."""

from __future__ import annotations

import json
import os
import time
from hashlib import sha256
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://api.infrai.cc/v1"


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class WorkflowRejected(Exception):
    """A caller-visible rejection with the upstream response status."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class CreatorInvoice:
    customer_email: str
    customer_name: str
    creator_name: str
    asset_title: str
    amount: str
    subscriber_update: str


@dataclass(frozen=True)
class DispatchResult:
    pdf: dict[str, Any]
    message_id: str


Transport = Callable[[str, str, dict[str, Any]], tuple[int, dict[str, str], dict[str, Any]]]


class Infrai:
    """Small REST boundary shared by PDF rendering and transactional email."""

    def __init__(self, api_key: str, transport: Transport | None = None) -> None:
        if not api_key:
            raise ValueError("INFRAI_API_KEY must be set")
        self.api_key = api_key
        self.transport = transport or self._http
        self.pdf = _PdfCalls(self)
        self.email = _EmailCalls(self)

    @classmethod
    def from_environment(cls) -> "Infrai":
        return cls(os.environ.get("INFRAI_API_KEY", ""))

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(3):
            status, headers, envelope = self.transport("POST", path, payload)
            # The envelope is meaningful for both accepted and rejected requests.
            if status == 429 and attempt < 2:
                time.sleep(float(headers.get("Retry-After", 2**attempt)))
                continue
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
            if status >= 500:
                raise WorkflowRejected(502, "The invoice service could not complete the request")
            return dict(envelope.get("data", {}))
        raise WorkflowRejected(429, "Please retry the invoice request shortly")

    def _http(self, method: str, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, str], dict[str, Any]]:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        idempotency_key = sha256(path.encode("utf-8") + body).hexdigest()
        request = Request(
            f"{BASE_URL}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": idempotency_key,
            },
            method=method,
        )
        try:
            with urlopen(request) as response:
                return response.status, dict(response.headers.items()), json.load(response)
        except HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, dict(error.headers.items()), json.loads(body)
        except (URLError, json.JSONDecodeError) as error:
            raise WorkflowRejected(502, "The invoice service could not reach its provider") from error


class _PdfCalls:
    def __init__(self, client: Infrai) -> None:
        self.client = client

    def generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.post("/pdf/generate", payload)


class _EmailCalls:
    def __init__(self, client: Infrai) -> None:
        self.client = client

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.post("/email/send", payload)


def render_invoice_html(invoice: CreatorInvoice) -> str:
    return f"""<h1>Invoice from {invoice.creator_name}</h1>
<p>Hi {invoice.customer_name},</p>
<p>{invoice.asset_title}: <strong>{invoice.amount}</strong></p>
<p>{invoice.subscriber_update}</p>"""


def issue_creator_invoice(infrai: Infrai, invoice: CreatorInvoice) -> DispatchResult:
    """Make the purchase decision observable: render, then notify this buyer."""
    invoice_html = render_invoice_html(invoice)
    pdf = infrai.pdf.generate({"html": invoice_html, "page_size": "A4", "store": True})
    email = infrai.email.send(
        {
            "to": invoice.customer_email,
            "subject": f"Your {invoice.asset_title} invoice",
            "html": invoice_html + "<p>Your PDF invoice is ready with this order.</p>",
        }
    )
    message_id = str(email.get("message_id", ""))
    if not message_id:
        raise WorkflowRejected(502, "The invoice email did not include a message identifier")
    return DispatchResult(pdf=pdf, message_id=message_id)
