"""Runnable example entry point for a creator's paid digital asset."""

from invoice_dispatch import CreatorInvoice, Infrai, WorkflowRejected, issue_creator_invoice


def main() -> None:
    invoice = CreatorInvoice(
        customer_email="chenhua@changba.com",
        customer_name="Avery",
        creator_name="Mina Studio",
        asset_title="Prompt Workflow Kit",
        amount="$24.00",
        subscriber_update="Your subscriber library now includes the latest workflow notes.",
    )
    try:
        result = issue_creator_invoice(Infrai.from_environment(), invoice)
    except WorkflowRejected as error:
        print(f"invoice request rejected ({error.status}): {error}")
        return
    print(f"invoice generated and email accepted: {result.message_id}")


if __name__ == "__main__":
    main()
