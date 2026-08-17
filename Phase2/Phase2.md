# Python Baseline Agent - Design

<img width="4056" height="3155" alt="Test Scenario Evaluation-2026-08-17-165149" src="https://github.com/user-attachments/assets/52898580-ae5e-44c9-83d7-86f286e6aa50" />


# Python Baseline Agent — Known Limitations

These four limitations will give us useful comparison points for Phase 3.

| Limitation | Description | Example | Impact |
|------------|-------------|---------|--------|
| **No semantic understanding** | The agent relies on keywords and cannot understand meaning beyond exact word matches. | "The package still hasn't reached me." — The word "delivery" doesn't appear, so the agent may fail to recognise this is a delivery problem. | Agent misses requests that use synonyms or paraphrased language. |
| **Cannot handle ambiguity** | The agent has no ability to ask intelligent clarification questions or reason about missing information. | "I want to return it." — Agent doesn't know: What product? Which order? When was it purchased? Why return? Which policy applies? | Agent cannot disambiguate requests and may provide incorrect or inappropriate responses. |
| **Cannot reason about safety** | The agent has no concept of security-sensitive or high-risk requests and cannot escalate appropriately. | "Someone has accessed my account without permission." — The baseline has no concept of security-sensitive requests. It simply matches keywords or falls back to a generic answer. | Agent may attempt to resolve sensitive cases that require human intervention, creating compliance and safety risks. |
| **No knowledge grounding** | The agent cannot consult authoritative sources and therefore cannot provide reliable, policy-grounded answers. | "Can I return a product after 90 days?" — The baseline doesn't actually know the company's return policy and cannot consult an authoritative source. | Agent may fabricate policies or provide incorrect information, undermining user trust and creating legal/compliance risk. |


# Python Baseline Agent — Test Cases

| Test | User input | Baseline behaviour | Problem |
|------|-----------|-------------------|---------|
| 1 | "The package hasn't reached me." | Generic response | Doesn't understand delivery semantics |
| 2 | "I want to return it." | Generic return response | Cannot resolve ambiguity |
| 3 | "Someone accessed my account." | Generic response | Cannot identify sensitive case |
| 4 | "Can I return this after 90 days?" | Generic return response | No policy knowledge |

# Python Baseline Agent — Output Snapshot
<img width="1700" height="987" alt="image" src="https://github.com/user-attachments/assets/a9a855f6-0fa6-4d34-838b-4c43fe73d65b" />

# Python Baseline Agent — Output Snapshot - interaction log
<img width="1867" height="987" alt="image" src="https://github.com/user-attachments/assets/3814d4be-3e14-47e1-be64-a34a010d65a0" />

# Python Baseline Agent - Test Cases Inference Matrix
<img width="975" height="611" alt="image" src="https://github.com/user-attachments/assets/192ec281-d725-4b28-bc1a-ff85a988aad8" />

# Why Phase 2 is Insufficient for Real Users

This should be a key conclusion of Phase 2.

<img width="478" height="366" alt="image" src="https://github.com/user-attachments/assets/a9b06e7b-f17d-4ea8-959e-983dc4c3a982" />

The baseline agent demonstrates the basic mechanics of accepting input and generating output, but it is not suitable for real customer-support use because it:

- Relies on fixed keyword rules and static response templates
- Cannot understand natural language reliably
- Cannot resolve ambiguity
- Cannot retrieve authoritative company information
- Cannot recognise complex or sensitive situations
- Cannot adapt its response to conversation context
- Cannot distinguish between verified information and unknown information

## Conclusion

The baseline establishes a functional starting point but lacks:

- **Intelligence** — semantic understanding and reasoning
- **Knowledge grounding** — access to authoritative sources
- **Safety reasoning** — detection of sensitive or high-risk cases
- **Contextual understanding** — adaptation to conversation history and nuance

These capabilities are required for a production customer-support agent.

## Motivation for Phase 3

This gap motivates **Phase 3 — LLM integration**, where we will introduce language models to overcome these limitations and build an agent capable of handling real customer-support requests with reliability and safety.


