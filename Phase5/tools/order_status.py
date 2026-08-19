from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data
import re


class OrderStatusTool(Component):
    display_name = "Order Status Tool"

    description = """
    Retrieve the operational status of a specific customer order.

    ALWAYS use this tool when the user asks about:
    - order status
    - shipment status
    - delivery status
    - where an order is
    - whether an order has shipped
    - whether an order has been delivered
    - expected delivery of an order

    Examples:
    - Where is order ORD1001?
    - Order status of ORD1001
    - Has ORD1001 shipped?
    - Has ORD1001 been delivered?
    - When will ORD1001 arrive?

    The required order_id format is ORD followed by 4 digits.

    Do not use this tool for greetings, return-policy questions,
    account-security questions, or unrelated customer-support requests.
    """

    icon = "PackageSearch"
    name = "OrderStatusTool"
    
    inputs = [
    MessageTextInput(
        name="order_id",
        display_name="Order ID",
        info="""
        The customer's order identifier.
        Extract it from the user's request.
        Expected format: ORD followed by 4 digits, for example ORD1001.
        """,
        tool_mode=True,
    ),
    ]

    outputs = [
        Output(
            display_name="Order Status",
            name="order_status",
            method="get_order_status",
        ),
    ]

    def get_order_status(self) -> Data:

        # Simulated operational order database
        orders = {
            "ORD1001": {
                "status": "Shipped",
                "carrier": "DHL",
                "estimated_delivery": "2026-08-20"
            },
            "ORD1002": {
                "status": "Delivered",
                "carrier": "PostNL",
                "estimated_delivery": "2026-08-16"
            },
            "ORD1003": {
                "status": "Processing",
                "carrier": "Not assigned",
                "estimated_delivery": "Not available"
            }
        }

        order_id = (self.order_id or "").strip().upper()

        # Guardrail 1: Missing order ID
        if not order_id:
            return Data(data={
                "success": False,
                "error": "missing_order_id",
                "message": "An order ID is required."
            })

        # Guardrail 2: Validate order ID format
        if not re.fullmatch(r"ORD\d{4}", order_id):
            return Data(data={
                "success": False,
                "error": "invalid_order_format",
                "message": "Order ID must use the format ORD followed by 4 digits."
            })

        # Guardrail 3: Order not found
        if order_id not in orders:
            return Data(data={
                "success": False,
                "error": "order_not_found",
                "order_id": order_id,
                "message": "The order was not found."
            })

        result = {
            "success": True,
            "order_id": order_id,
            **orders[order_id]
        }

        self.status = result

        return Data(data=result)