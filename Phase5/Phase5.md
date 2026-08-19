# Phase 5: Enable Tool Usage

## 1. Objective

The objective of Phase 5 is to extend the AI Customer Support Agent with
tool-calling capabilities.

The agent should be able to:

- Understand the customer's request.
- Decide whether a tool is required.
- Select the correct tool.
- Pass the required arguments to the tool.
- Use the returned result to generate the response.
- Handle tool errors safely.
- Avoid unnecessary or repeated tool calls.

For this phase, two tools are implemented:

1. `GET_ORDER_STATUS`
2. `CREATE_ESCALATION`

The RAG capability developed in Phase 4 remains a separate knowledge-retrieval
implementation and is not included as an Agent tool in the final Phase 5 design.


---

## 2. Phase 5 Architecture
<img width="635" height="898" alt="image" src="https://github.com/user-attachments/assets/53336d82-341b-464e-b9c7-fbf7c3875372" />

## 3. Phase 5 Tools

### 1. GET_ORDER_STATUS

The `GET_ORDER_STATUS` tool retrieves the simulated status of a specific customer order using a valid order ID.

**Purpose:**
- Check order status
- Check shipment status
- Determine whether an order has shipped or been delivered
- Retrieve estimated delivery information

**Example:**
`Where is order ORD1001?`

---

### 2. CREATE_ESCALATION

The `CREATE_ESCALATION` tool escalates sensitive, high-risk, or unresolved customer-support cases to a human support representative.

**Purpose:**
- Handle unauthorised account access
- Handle suspected account compromise or security incidents
- Escalate cases that require human intervention
- Create a simulated support escalation ticket

**Example:**
`Someone accessed my account without permission.`

---

Together, these tools allow the Agent to choose between **operational order lookup** and **human escalation** based on the customer's request.
