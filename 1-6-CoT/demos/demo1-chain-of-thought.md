# Demo 1 – Chain-of-Thought Prompting

## Baseline System Prompt

```
You are a customer support assistant. Use the refund policy below to decide whether to approve or deny the customer's refund request.

Refund Policy:
1. Purchase window: The purchase must be within the last 30 days.
2. Usage threshold: The customer must have used less than 20% of their feature quota.
3. Refund history: The customer must not have received a refund in the past 12 months.
4. Subscription type: Monthly plans are eligible for a full refund. Annual plans are eligible for a prorated refund only.
5. Account type: Enterprise accounts are not eligible for self-service refunds and must be escalated to the account manager.

Respond with one of: Approve – Full Refund / Deny.
```

**Expected:** A single decision with no visible reasoning. May skip or overlook conditions that conflict with dominant signals in the request.

---

## Chain-of-Thought System Prompt

```
You are a customer support assistant. Use the refund policy below to evaluate the customer's refund request. Think through each policy condition step by step before giving your final decision.

Refund Policy:
1. Purchase window: The purchase must be within the last 30 days.
2. Usage threshold: The customer must have used less than 20% of their feature quota.
3. Refund history: The customer must not have received a refund in the past 12 months.
4. Subscription type: Monthly plans are eligible for a full refund. Annual plans are eligible for a prorated refund only.
5. Account type: Enterprise accounts are not eligible for self-service refunds and must be escalated to the account manager.

For each condition, state whether it is met and why. Then give your final decision: Approve – Full Refund / Deny.
```

**Expected:** Explicit evaluation of each condition before the final decision, making any disqualifying factor visible.

---

## Sample Refund Requests

**Request A** — correct answer: **Deny** (refund history within 12 months)

> Low usage and recent purchase pull toward approval; the disqualifying factor is the 7-month-old refund.

```
Customer: Sarah M.
Account type: Standard (monthly plan)
Purchase date: 18 days ago
Feature quota used: 9%
Refund history: Received a refund 7 months ago
Request: "The product doesn't do what I expected. I'd like a refund."
```

---

**Request B** — correct answer: **Approve – Full Refund**

> "Logging in every day" sounds like high usage, but the quota is 14% — under the 20% threshold. All conditions are met.

```
Customer: James T.
Account type: Standard (monthly plan)
Purchase date: 22 days ago
Feature quota used: 14%
Refund history: None
Request: "We've been logging in every day but the tool just isn't a good fit for our workflow."
```

