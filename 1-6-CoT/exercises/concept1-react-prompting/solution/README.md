# Exercise Solution – Restaurant Recommendation Agent

## Agent Instruction

```
You are a helpful restaurant recommendation assistant. When a user asks for a restaurant recommendation, always use the available tools to discover what cuisines and restaurants are available — never assume. Base your recommendation on the tool results, not on assumptions. If the first restaurant has no availability, check the next best option before responding.

You are an agent for a single city where the user is located, no need to ask where a user is located.
```

---

## Action Group

> **Note – underscores in function names:** Function names must use underscores (`_`), not hyphens (`-`). Bedrock agents may fail to invoke functions whose names contain hyphens. Action group names can use hyphens, but function names inside them must not.

Action group name: `restaurant-tools`

### `get_cuisines`

Returns the list of cuisine types available. Takes no parameters.

### `search_restaurants`

| Parameter | Type   | Required | Description                                                              |
|-----------|--------|----------|--------------------------------------------------------------------------|
| `cuisine` | string | No       | The cuisine type (e.g. Italian, Japanese). If omitted, all are returned. |

### `get_availability`

| Parameter       | Type   | Required | Description                     |
|-----------------|--------|----------|---------------------------------|
| `restaurant_id` | string | Yes      | The unique ID of the restaurant |

---

## Test Prompt

```
Find me an Italian restaurant for tonight.
```

---

## Expected Agent Behavior

1. The agent calls `get_cuisines` to discover available cuisine types
2. The agent calls `search_restaurants` with `cuisine=Italian` and receives `Trattoria Bella` (r1) and `Osteria Romana` (r2)
3. The agent calls `get_availability` with `restaurant_id=r1` — `Trattoria Bella` has availability
4. The agent presents `Trattoria Bella` as the recommendation
5. If the agent tries `Osteria Romana` (r2) first, it will find no availability and fall back to `Trattoria Bella`

---

## Cleanup

When you are done with the exercise, delete the CloudFormation stack to avoid ongoing charges:

```bash
aws cloudformation delete-stack --stack-name restaurant-agent --region us-east-1
```

You can also delete the Bedrock Agent from the Amazon Bedrock console.
