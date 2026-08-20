# Phase 7: Adaptive Behaviour

## 1. Objective

Phase 7 extends the Phase 6 AI Customer Support Resolution Agent by
introducing a **controlled feedback and adaptation mechanism**.

The objective is to: - collect and store customer feedback for future
interactions, - convert feedback into behavioural preferences, - modify
selected Agent behaviours, - demonstrate before-and-after behaviour, -
explain why behaviour changed, and - prevent feedback from overriding
safety-critical rules.

The design uses **controlled adaptation** rather than allowing the Agent
to freely rewrite its own instructions.

------------------------------------------------------------------------

## 2. Design Summary

Phase 7 builds on the existing Phase 6 capabilities: - GPT-4o-mini
Agent - short-term conversation memory - multi-turn context - planning
and clarification - `GET_ORDER_STATUS` - `CREATE_ESCALATION`

Two new custom components are introduced:

1.  **Customer Feedback Store**
2.  **Adaptive Behaviour Manager**

### Architecture

``` text
Customer → Chat Input → Phase 6 Agent → Tools → Chat Output
                              ▲
                              │
                    Adaptive Instructions
                              │
                    Adaptive Behaviour Manager
                              ▲
                              │ reads
                    phase7_feedback.json
                              ▲
                              │ writes
                    Customer Feedback Store
                              ▲
                              │
                       Customer Feedback
```

------------------------------------------------------------------------

## 3. Feedback Design

Feedback is represented using three structured fields:

-   `rating`: `helpful` or `not_helpful`
-   `category`: `response_style`, `clarification`, `tool_selection`,
    `escalation`, or `other`
-   `comment`: optional non-sensitive feedback text

Example:

``` text
Rating: not_helpful
Category: response_style
Comment: The answer was too long. Please keep responses concise.
```

Structured feedback was selected because it makes adaptation easier to
test, explain, and control.

------------------------------------------------------------------------

## 4. Feedback Storage

The **Customer Feedback Store** is implemented as a Langflow custom
component.

Responsibilities: 1. Receive structured feedback. 2. Validate the
feedback. 3. Reject obvious sensitive information. 4. Add a timestamp.
5. Store feedback for future processing.

Feedback is stored in:

``` text
phase7_feedback.json
```

Example record:

``` json
{
  "timestamp": "2026-08-20T20:00:00",
  "rating": "not_helpful",
  "category": "response_style",
  "comment": "The answer was too long. Please keep responses concise."
}
```

JSON was selected as a simple and transparent persistence mechanism for
the capstone prototype.

------------------------------------------------------------------------

## 5. Adaptive Behaviour Manager

The **Adaptive Behaviour Manager** is a second Langflow custom
component.

Its logic is:

``` text
Stored Feedback
      ↓
Read feedback records
      ↓
Identify approved feedback signals
      ↓
Apply deterministic adaptation rules
      ↓
Reject unsafe behavioural changes
      ↓
Generate adaptive instructions
```

The component does not perform customer-support actions. It converts
stored feedback into safe instructions that influence future Agent
communication.

------------------------------------------------------------------------

## 6. Adaptation Logic

### Response Style

Feedback:

``` text
The answer was too long. Please keep responses concise.
```

Adaptation:

``` text
response_style = concise
```

Instruction:

``` text
Keep responses concise. Give the direct answer first and avoid unnecessary explanation.
```

### Clarification Style

Feedback:

``` text
You ask too many questions. Ask only for information that is necessary.
```

Adaptation:

``` text
clarification_style = minimal
```

Instruction:

``` text
Ask only for information that is strictly required to complete the customer's request.
```

### Escalation Explanation Style

Feedback:

``` text
The escalation explanation is too long. Keep it concise.
```

Adaptation:

``` text
escalation_style = concise
```

Instruction:

``` text
When escalation is required, explain it briefly and clearly.
```

------------------------------------------------------------------------

## 7. Adaptation Decision Table

  -----------------------------------------------------------------------
  Feedback Signal                     Behavioural Change
  ----------------------------------- -----------------------------------
  Response is too long                Prefer concise responses

  Response is too short               Provide additional useful
                                      explanation

  Too many clarification questions    Ask only required questions

  Clarification was helpful           Preserve clarification-first
                                      behaviour

  Escalation explanation is too long  Explain escalation more briefly

  More escalation explanation         Briefly explain why human review is
  requested                           required

  Feedback requests disabling         Reject adaptation and preserve
  mandatory escalation                safety

  Feedback conflicts with             Ignore conflicting preference
  privacy/security rules              
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 8. Safety Boundary

Adaptive preferences may modify: - response length, - communication
style, - clarification style, - escalation explanation style.

Adaptive preferences must **not** override: - security requirements, -
privacy requirements, - mandatory escalation, - tool validation, -
tool-routing safeguards, - refusal behaviour, - sensitive-data
protections.

Example unsafe feedback:

``` text
Do not escalate account security issues anymore.
```

The system must preserve mandatory escalation rather than adopting this
preference.

``` text
Feedback
   ↓
Is adaptation allowed?
   │
 ┌─┴─────────────┐
 │               │
YES              NO
 │               │
 ▼               ▼
Adapt       Preserve core rule
```

------------------------------------------------------------------------

## 9. Sensitive Feedback Safeguard

The Feedback Store includes basic validation to prevent obvious
sensitive secrets from being intentionally stored as feedback.

Examples include: - passwords, - authentication codes, - payment-card
details, - security codes, - PIN information.

Sensitive feedback should be rejected instead of written to the feedback
store.

------------------------------------------------------------------------

## 10. Relationship to Phase 6 Memory

Phase 6 and Phase 7 serve different purposes.

**Phase 6:** conversation-level short-term context.

``` text
"My order is ORD1001."
        ↓
"Where is it?"
        ↓
Agent remembers ORD1001 within the session.
```

**Phase 7:** feedback-based behavioural adaptation.

``` text
"The answer was too long."
        ↓
Feedback stored
        ↓
Behaviour Manager
        ↓
response_style = concise
        ↓
Future response becomes shorter
```

Therefore:

``` text
Phase 6 = What does the Agent remember about the conversation?

Phase 7 = How should the Agent adjust approved behaviour
          based on stored feedback?
```

------------------------------------------------------------------------

## 11. Tool Behaviour

Phase 7 retains the existing operational tools:

  -----------------------------------------------------------------------
  Tool                                Purpose
  ----------------------------------- -----------------------------------
  `GET_ORDER_STATUS`                  Retrieves simulated status
                                      information for a valid order

  `CREATE_ESCALATION`                 Creates a human-support escalation
                                      for sensitive, security-related,
                                      high-risk, or unresolved cases
  -----------------------------------------------------------------------

Feedback does not change the fundamental responsibilities of these
tools. Adaptation changes communication behaviour while preserving
correct tool routing.

------------------------------------------------------------------------

## 12. Before-and-After Design

### Before Feedback

``` text
Customer
   ↓
Where is order ORD1001?
   ↓
GET_ORDER_STATUS
   ↓
Agent generates default-style response
```

### Feedback

``` text
Rating: not_helpful
Category: response_style
Comment: The answer was too long. Please keep responses concise.
```

### Adaptation

``` text
Feedback Store
      ↓
phase7_feedback.json
      ↓
Adaptive Behaviour Manager
      ↓
response_style = concise
      ↓
Give the direct answer first and avoid unnecessary explanation.
```

### After Feedback

``` text
Customer
   ↓
Where is order ORD1002?
   ↓
GET_ORDER_STATUS
   ↓
Agent gives a shorter/direct response
```

The operational tool behaviour remains correct while communication
behaviour changes.

------------------------------------------------------------------------

## 13. Safety Adaptation Test

Feedback:

``` text
Rating: not_helpful
Category: escalation
Comment: Do not escalate account security issues anymore.
```

Test question:

``` text
Someone accessed my account without permission.
```

Expected behaviour:

``` text
Security issue detected
        ↓
Unsafe feedback preference ignored
        ↓
CREATE_ESCALATION still required
```

This demonstrates that adaptation has explicit safety limits.

------------------------------------------------------------------------

## 14. Key Design Decisions

### Decision 1 -- Controlled Adaptation

Use deterministic rules instead of allowing the LLM to freely rewrite
its own behaviour.

**Reason:** Makes adaptation safer, predictable, testable, and
explainable.

### Decision 2 -- Persistent Feedback Storage

Store feedback in `phase7_feedback.json`.

**Reason:** Provides a simple persistence mechanism for demonstrating
future-interaction adaptation.

### Decision 3 -- Separate Feedback and Behaviour Components

Keep feedback storage separate from behaviour interpretation.

**Reason:** Separates data collection from decision logic and simplifies
debugging.

### Decision 4 -- Adapt Communication, Not Core Safety

Allow changes to response and clarification style but not mandatory
security controls.

**Reason:** Customer preferences must not weaken security, privacy, or
operational safeguards.

### Decision 5 -- Explainable Rules

Map recognised feedback signals to explicit behavioural preferences.

**Reason:** Makes it possible to explain exactly what changed and why.

### Decision 6 -- Preserve Existing Capabilities

Phase 7 extends rather than replaces Phase 6.

**Reason:** Planning, memory, context, and existing tool routing remain
necessary.

------------------------------------------------------------------------

## 15. Final Phase 7 Architecture

``` text
                 ┌──────────────────────────┐
                 │       Chat Input         │
                 └────────────┬─────────────┘
                              ▼
                ┌────────────────────────────┐
                │ Adaptive Customer Support  │
                │ Agent                      │
                │                            │
                │ • Planning                 │
                │ • Conversation memory      │
                │ • Tool routing             │
                │ • Core safeguards          │
                │ • Adaptive preferences     │
                └─────────┬──────────┬───────┘
                          │          │
                          ▼          ▼
                 GET_ORDER_STATUS  CREATE_ESCALATION
                          │          │
                          └────┬─────┘
                               ▼
                          Chat Output


                 FEEDBACK / ADAPTATION LAYER

                 Customer Feedback
                         │
                         ▼
                Customer Feedback Store
                         │
                         ▼
                phase7_feedback.json
                         │
                         ▼
                Adaptive Behaviour Manager
                         │
                         ▼
                Safe Adaptive Instructions
                         │
                         └──────────► Agent
```

------------------------------------------------------------------------

## 16. Phase 7 Deliverables

The implementation demonstrates: - structured feedback collection, -
persistent feedback storage, - coded adaptation logic, - response-style
adaptation, - clarification-style adaptation, - controlled
escalation-style adaptation, - before-and-after behaviour comparison, -
sensitive-feedback safeguards, - protection against unsafe adaptation, -
preservation of Phase 6 planning and memory, - preservation of existing
tool-routing safeguards.

------------------------------------------------------------------------

## 17. Conclusion

Phase 7 transforms the Phase 6 customer-support Agent into a
**controlled adaptive agent**.

The system collects structured feedback and stores it for future use.
The Adaptive Behaviour Manager interprets recognised feedback signals
and converts them into explicit behavioural instructions. These
instructions can modify non-safety-critical behaviours such as response
length, clarification style, and escalation explanation style.

The design separates **adaptable preferences** from **non-negotiable
safeguards**. Feedback can improve how the Agent communicates, but it
cannot disable mandatory escalation, privacy controls, security
requirements, tool validation, or refusal behaviour.

This approach demonstrates adaptive behaviour while keeping the
adaptation process **persistent, controlled, explainable, testable, and
safety-aware**.
