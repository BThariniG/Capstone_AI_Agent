import logging
from datetime import datetime


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    filename="agent_interactions.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# --------------------------------------------------
# Baseline response rules
# --------------------------------------------------

def generate_response(user_input):
    """
    Generate a response using simple keyword-based rules.
    This is intentionally a baseline implementation.
    """

    text = user_input.lower().strip()

    # Greeting
    if any(word in text for word in ["hello", "hi", "hey"]):
        return "Hello! How can I help you with your support request?"

    # Return-related request
    elif any(word in text for word in ["return", "returns"]):
        return (
            "For return-related questions, please check the company's "
            "return policy or contact customer support."
        )

    # Delivery-related request
    elif any(word in text for word in ["delivery", "delivered", "shipping", "shipment"]):
        return (
            "For delivery-related questions, please check your order "
            "tracking information or contact customer support."
        )

    # Refund-related request
    elif any(word in text for word in ["refund", "money back"]):
        return (
            "Refund requests are handled according to the company's "
            "refund policy. Please contact customer support for assistance."
        )

    # Default response
    else:
        return (
            "I'm sorry, I don't have enough information to answer that "
            "question. Please contact customer support."
        )


# --------------------------------------------------
# Agent interaction
# --------------------------------------------------

def run_agent(user_input):
    """
    Process one user interaction and log the result.
    """

    response = generate_response(user_input)

    # Privacy-safe logging: This will later become evidence for the PII-safe logging requirement.
    # We deliberately do not log the user's actual message.
    logging.info(
        "interaction_completed | response_category_generated"
    )

    return response


# --------------------------------------------------
# Command-line interface
# --------------------------------------------------

def main():

    print("AI Customer Support Baseline Agent")
    print("Type 'exit' to stop.\n")

    while True:

        user_input = input("Customer: ")

        if user_input.lower().strip() == "exit":
            print("Agent: Goodbye!")
            break

        response = run_agent(user_input)

        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()