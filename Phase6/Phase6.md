# Phase 6: Planning, Memory & Context

## 1. Objective

Phase 6 extends the AI Customer Support Agent developed in Phase 5 by
adding **multi-step planning, conversation memory, and contextual
awareness**.

The goal is to allow the Agent to handle multi-turn customer
conversations without repeatedly asking for information that has already
been provided.

------------------------------------------------------------------------

## 2. Phase 6 Design

The Phase 5 Agent is extended with:

-   Short-term conversation memory
-   Multi-turn context handling
-   Multi-step planning logic
-   Context-aware tool selection
-   Memory retention and reset rules

### Architecture

``` text
                    ┌─────────────────────┐
                    │   Customer Query    │
                    └──────────┬──────────┘
                               │
                               ▼
                         ┌────────────┐
                         │ Chat Input │
                         └─────┬──────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │   Langflow Agent       │
                  │     GPT-4o-mini        │
                  │                        │
                  │ • Planning Logic       │
                  │ • Conversation Context │
                  │ • Short-Term Memory    │
                  │ • Tool Routing         │
                  └───────────┬────────────┘
                              │
                 ┌────────────┴─────────────┐
                 │                          │
                 ▼                          ▼
        ┌──────────────────┐       ┌───────────────────┐
        │ GET_ORDER_STATUS │       │ CREATE_ESCALATION │
        └────────┬─────────┘       └─────────┬─────────┘
                 │                           │
                 └────────────┬──────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Final Response   │
                    └───────────────────┘

                  Conversation History
                         ↕
                 Same Session Context
```

------------------------------------------------------------------------

## 3. Planning Design

Before responding, the Agent determines:

1.  What the customer wants.
2.  What information is already available in the conversation.
3.  Whether required information is missing.
4.  Whether a tool is required.
5.  Which tool should be selected.
6.  Whether additional action or escalation is required.

### Example

``` text
Customer:
"I have a problem with my order."
        ↓
Agent detects missing order ID
        ↓
Requests order ID
        ↓
Customer:
"ORD1001"
        ↓
Agent remembers original intent
        ↓
GET_ORDER_STATUS
        ↓
Tool Result
        ↓
Customer Response
```

This enables the Agent to continue a task across multiple conversation
turns.

------------------------------------------------------------------------

## 4. Short-Term Memory Design

The Agent uses Langflow's conversation history to maintain context
within the current session.

The Agent is configured to use recent chat-history messages so that
information provided earlier can be reused during follow-up requests.

### Example

``` text
Turn 1:
Customer: "My order number is ORD1001."

              ↓ Memory

Turn 2:
Customer: "Where is it?"

              ↓

Agent resolves:
"it" = ORD1001

              ↓

GET_ORDER_STATUS("ORD1001")
```

Without conversation memory, the Agent would need to ask the customer
for the order number again.

------------------------------------------------------------------------

## 5. Memory Retention and Reset

### Retained Within the Current Session

The Agent may use relevant short-term information such as:

-   Order ID
-   Current support request
-   Clarification responses
-   Relevant tool results
-   Current escalation context

### Sensitive Information

The Agent should not request or intentionally retain unnecessary
sensitive information such as:

-   Passwords
-   Authentication codes
-   Payment-card information
-   Security credentials

### Memory Reset

Conversation context is associated with the current session.

``` text
Session A
─────────
"My order is ORD1001"
        ↓
"Where is it?"
        ↓
ORD1001 remembered ✓


New Session
───────────
"Where is it?"
        ↓
No previous order context
        ↓
Agent requests order ID ✓
```

A new session therefore provides a clean conversation context.

------------------------------------------------------------------------

## 6. Message History

The Langflow Agent uses its built-in chat-history capability for
short-term conversation memory.

The Agent is configured with:

``` text
Number of Chat History Messages = 10
```

A separate `Message History` component can be used in **Retrieve** mode
to inspect stored conversation messages and provide evidence of memory
behaviour.

It does not need to be directly connected to the Agent because the Agent
already uses its built-in conversation history.

------------------------------------------------------------------------

## 7. Phase 6 Tools

Phase 6 retains the two operational tools developed in Phase 5.

  -----------------------------------------------------------------------
  Tool                                Purpose
  ----------------------------------- -----------------------------------
  `GET_ORDER_STATUS`                  Retrieves the simulated status of a
                                      specific customer order

  `CREATE_ESCALATION`                 Escalates sensitive, high-risk, or
                                      unresolved cases to human support
  -----------------------------------------------------------------------

Conversation context helps the Agent determine when and how these tools
should be used during multi-turn interactions.

------------------------------------------------------------------------

## 8. Design Improvement

### Before Phase 6

``` text
Customer Question
      ↓
Agent
      ↓
Single-turn decision
      ↓
Tool / Response
```

### After Phase 6

``` text
Multi-turn Conversation
          ↓
Conversation Context
          ↓
Agent Planning
          ↓
Identify Known/Missing Information
          ↓
Select Required Action
          ↓
Tool Execution
          ↓
Evaluate Result
          ↓
Continue Conversation
```

Phase 6 therefore improves the Agent from a primarily **single-turn
tool-using assistant** into a **context-aware, multi-turn
customer-support agent** capable of retaining relevant conversation
information and planning the next action.
