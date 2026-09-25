from invoice_dispatch import CreatorInvoice, Infrai, issue_creator_invoice


def test_paid_asset_renders_before_customer_notification() -> None:
    calls = []

    def transport(method, path, payload):
        calls.append((method, path, payload))
        if path == "/pdf/generate":
            return 201, {}, {"ok": True, "data": {"pdf_id": "pdf_123"}}
        return 202, {}, {"ok": True, "data": {"message_id": "msg_456"}}

    invoice = CreatorInvoice(
        customer_email="buyer@example.com",
        customer_name="Buyer",
        creator_name="Northline Audio",
        asset_title="Mixing Presets",
        amount="$18.00",
        subscriber_update="The download is now part of your subscriber collection.",
    )

    result = issue_creator_invoice(Infrai("test-key", transport), invoice)

    assert result.message_id == "msg_456"
    assert [call[1] for call in calls] == ["/pdf/generate", "/email/send"]
    assert calls[0][2]["html"] in calls[1][2]["html"]
    assert calls[1][2]["to"] == "buyer@example.com"
