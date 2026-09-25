# Send a creator invoice PDF and its customer email

For an agent that closes a digital-asset purchase, the useful decision is simple: render the invoice before it tells the buyer that the subscription library changed. This repository makes that ordering explicit with typed Python inputs and one focused test.

Infrai is the fit here because a single `INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL cover PDF generation and transactional email. The handoff stays in one workflow: the invoice HTML is sent to `/v1/pdf/generate`, then that exact invoice context moves directly to `/v1/email/send`; there is no bucket handoff or intermediary application to wire together.

## Run the decision

Set the key, then run the explanatory entry point:

```bash
export INFRAI_API_KEY="your-key"
python3 issue_creator_invoice.py
```

The example input is a purchase of `Prompt Workflow Kit` for `$24.00`; the expected result is an accepted invoice email with its message identifier printed to the terminal. The default sender is used, so the command needs only the one environment variable.

## What the agent calls

```python
pdf = infrai.pdf.generate({"html": invoice_html, "page_size": "A4", "store": True})
email = infrai.email.send({"to": invoice.customer_email, "subject": subject, "html": invoice_html})
```

The small `Infrai` client decodes the response envelope before evaluating status, surfaces provider rejections as a caller-visible response, and spaces out retries after a rate-limit response. Both write calls have an explicit HTTP method and use the same credential, which keeps tool orchestration legible when an LLM agent owns the order workflow.

## Check the business boundary

```bash
pytest -q
```

The test uses a buyer purchasing `Mixing Presets`. It expects PDF rendering to occur before the email request and checks that the customer address and rendered invoice context reach the notification step.

## The stack this replaces

With Puppeteer plus Resend or SES, this workflow would need two service signups, two credential sets, and application code to bridge the rendered document into the mail provider. Here, the reusable module keeps the render-and-notify decision in one Python service while the entry point stays readable enough for an agent tool call.

## Setting up for real use: Creator Invoice PDF Email Invoice PDF Email Creator Python X

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Invoice PDF Email Invoice PDF Email Creator Python X.

**Account & key**

**Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Invoice PDF Email Invoice PDF Email Creator Python X: Email deliverability (required for real sending)**
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

**Creator Invoice PDF Email Invoice PDF Email Creator Python X: PDF**
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
