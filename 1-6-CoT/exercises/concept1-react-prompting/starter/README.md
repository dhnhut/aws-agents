# Exercise – Restaurant Recommendation Agent

## Overview

In this exercise you will build a restaurant recommendation agent using Amazon Bedrock Agents. The Lambda functions that back the agent's tools are provided and ready to deploy. Your task is to deploy the infrastructure, create the agent, and wire everything together.

---

## Step 1 – Deploy the Lambda Functions

A CloudFormation template is provided in this folder to create functions for your agent. It creates three Lambda functions and grants Bedrock permission to invoke them:

- **get-cuisines** – returns the list of cuisine types available
- **search-restaurants** – returns restaurants, optionally filtered by cuisine
- **get-availability** – checks whether a specific restaurant has availability tonight

You would need to run the following command

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name restaurant-agent \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

---

## Step 2 – Create the Bedrock Agent

1. Open the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock) and navigate to **Agents**
2. Click **Create agent**
3. Under **Model**, select **Amazon Nova Pro**
4. Write an agent instruction that:
   - Describes it as a restaurant recommendation assistant
   - Tells it to always use tools before making suggestions
   - Tells it to base its recommendation on tool results, not assumptions

---

## Step 3 – Create the Action Groups

Bedrock only allows one Lambda function per action group. Create three separate action groups, one for each Lambda.

> **Warning – use underscores in function names:** When naming functions inside an action group, always use underscores (`_`), never hyphens (`-`). For example, use `get_cuisines`, not `get-cuisines`. Bedrock agents may fail to invoke a function whose name contains hyphens. Action group names (the container) can use hyphens, but the function names inside must not.

---

### Action Group 1: `get-cuisines`

1. In your agent, click **Add action group**
2. Name it `get-cuisines`
3. Under **Action group type**, choose **Define with function details**
4. Add a function named `get_cuisines`:
   - Description: Returns the list of cuisine types available
   - No parameters
5. Under **Action group invocation**, select the `get-cuisines` Lambda (ARN from the CloudFormation outputs)
6. Click **Save**

---

### Action Group 2: `search-restaurants`

1. Click **Add action group**
2. Name it `search-restaurants`
3. Under **Action group type**, choose **Define with function details**
4. Add a function named `search_restaurants`:
   - Description: Searches for restaurants. Returns all restaurants if no cuisine is specified.
   - Add parameter:

| Parameter | Type   | Required | Description                                                              |
|-----------|--------|----------|--------------------------------------------------------------------------|
| `cuisine` | string | No       | The cuisine type (e.g. Italian, Japanese). If omitted, all are returned. |

5. Under **Action group invocation**, select the `search-restaurants` Lambda (ARN from the CloudFormation outputs)
6. Click **Save**

---

### Action Group 3: `get-availability`

1. Click **Add action group**
2. Name it `get-availability`
3. Under **Action group type**, choose **Define with function details**
4. Add a function named `get_availability`:
   - Description: Checks whether a specific restaurant has availability for tonight.
   - Add parameter:

| Parameter         | Type   | Required | Description                         |
|-------------------|--------|----------|-------------------------------------|
| `restaurant_id`   | string | Yes      | The unique ID of the restaurant     |

5. Under **Action group invocation**, select the `get-availability` Lambda (ARN from the CloudFormation outputs)
6. Click **Save**

---

Once all three action groups are saved, click **Prepare** to rebuild the agent before testing.

---

## Step 4 – Test the Agent

Use this prompt:

```
Find me an Italian restaurant for tonight.
```

Observe how the agent calls tools in sequence before producing a final recommendation.

---

## Deliverable

- Your agent instruction prompt
- A screenshot or copy of the chat history showing the agent using the tools

---

## Cleanup

When you are done with the exercise, delete the CloudFormation stack to avoid ongoing charges:

```bash
aws cloudformation delete-stack --stack-name restaurant-agent --region us-east-1
```

You can also delete the Bedrock Agent from the Amazon Bedrock console.
