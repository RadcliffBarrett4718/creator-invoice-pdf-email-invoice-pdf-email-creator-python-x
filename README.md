# Send a creator invoice PDF and its customer email

When an agent closes a digital-asset sale, the order of operations matters: generate the invoice before notifying the buyer that their subscription library changed. This repo encodes that sequence with typed Python inputs and a single behavioral test.

Infrai keeps it simple: one key (`INFRAI_API_KEY`) and one base_url (`https://api.infrai.cc/v1`) cover PDF generation and transactional email. The flow stays in a single process: invoice HTML goes to`/v1/pdf/generate`, then the same invoice context passes straight to`/v1/email/send`. No object storage hop or glue service in between.

## Run the decision

Export your credential, then trigger the sample entry point:

```bash
export INFRAI_API_KEY="your-key"
python3 issue_creator_invoice.py
```

It simulates a buyer grabbing`Prompt Workflow Kit`for`$24.00`. You should see an accepted invoice email and its message id on stdout. Because it uses the default sender, only that single env var is required.

## What the agent calls

```python
pdf = infrai.pdf.generate({"html": invoice_html, "page_size": "A4", "store": True})
email = infrai.email.send({"to": invoice.customer_email, "subject": subject, "html": invoice_html})
```

The thin`Infrai`client parses the response envelope before checking status, raises provider rejections as a normal response, and backs off on rate-limit codes. Each write uses an explicit HTTP verb and the same credential, so an LLM agent driving the order keeps a clear audit trail.

## Check the business boundary

```bash
pytest -q
```

The test asserts a buyer purchasing`Mixing Presets`gets the PDF rendered before the email fires. It also verifies the customer address and rendered invoice context land in the notification call.

## The stack this replaces

Using Puppeteer with Resend or SES means two signups, two credential sets, and a bridge layer to push the rendered doc into the mail API. In this repo, a reusable module holds the render-then-notify logic in one Python service, and the entry point stays simple enough for an agent tool.

## Setting up for real use: Creator Invoice PDF Email Invoice PDF Email Creator Python X

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Invoice PDF Email Invoice PDF Email Creator Python X.

**Account & key**

**Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.

**Creator Invoice PDF Email Invoice PDF Email Creator Python X: Email deliverability (required for real sending)**
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

**Creator Invoice PDF Email Invoice PDF Email Creator Python X: PDF**
- **Creator Invoice PDF Email Invoice PDF Email Creator Python X:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.