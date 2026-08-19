from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data
import uuid


class HumanEscalationTool(Component):
    display_name = "Human Escalation Tool"

    description = """
    Escalate sensitive, high-risk, unresolved, or policy-exception
    customer support cases to a human support representative.

    ALWAYS use this tool for:
    - unauthorized account access
    - suspected fraud or account-security incidents
    - sensitive customer-security concerns
    - delivered-but-missing packages when policy requires escalation
    - return exceptions requiring human review
    - unresolved support cases that cannot be safely handled by the AI

    Do NOT use this tool for:
    - greetings
    - ordinary order-status requests
    - simple company-policy questions
    - routine return-policy questions that can be answered from approved knowledge
    """

    icon = "UserRound"
    name = "HumanEscalationTool"

    inputs = [
        MessageTextInput(
            name="issue_type",
            display_name="Issue Type",
            info="""
            Category of case requiring human escalation.
            Allowed values:
            account_security,
            delivery_issue,
            return_exception,
            unresolved_support.
            """,
            tool_mode=True,
        ),
        MessageTextInput(
            name="reason",
            display_name="Reason",
            info="""
            Short reason for escalation.
            Do not include passwords, payment-card information,
            security codes, or unnecessary personal information.
            """,
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Escalation Result",
            name="escalation_result",
            method="create_escalation",
        ),
    ]

    def create_escalation(self) -> Data:

        issue_type = (self.issue_type or "").strip().lower()
        reason = (self.reason or "").strip()

        allowed_types = {
            "account_security",
            "delivery_issue",
            "return_exception",
            "unresolved_support"
        }

        # Guardrail 1: Validate issue type
        if issue_type not in allowed_types:
            return Data(data={
                "success": False,
                "error": "unsupported_issue_type",
                "allowed_types": sorted(allowed_types)
            })

        # Guardrail 2: Require reason
        if not reason:
            return Data(data={
                "success": False,
                "error": "missing_reason"
            })

        # Guardrail 3: Detect obvious sensitive secrets
        blocked_terms = [
            "password",
            "credit card",
            "cvv",
            "security code",
            "pin number"
        ]

        if any(term in reason.lower() for term in blocked_terms):
            return Data(data={
                "success": False,
                "error": "sensitive_data_detected",
                "message": "Do not include authentication or payment secrets."
            })

        ticket_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"

        result = {
            "success": True,
            "ticket_id": ticket_id,
            "issue_type": issue_type,
            "status": "Escalated to human support"
        }

        self.status = result
        return Data(data=result)