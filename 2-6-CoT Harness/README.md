
# Exercise Solution: Restaurant Recommendation Agent


[CloudFormation converting to AgentCore Gateway](template.yaml)

### Deploy stack
```bash
aws-agents git:(main) ✗ aws configure --profile udacity
aws-agents git:(main) ✗ aws cloudformation deploy \    
  --template-file "2-6-CoT Harness/template.yaml" \
  --stack-name restaurant-agentcore-harness \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --profile udacity
```

###  Check the deployment status

![CloudFormation deploy status](assets/cloudformation.png)

### Lambda functions

![lambda](assets/lambda.png)


### Harness

![alt text](assets/harness.png)

#### Harness detail

![Harness detail](assets/harness_detail.png)

#### Gateway

![Gateway](assets/gateway.png)

### Test

![test prompt](assets/test.png)

### Tools calling results

![cuisine result](assets/cuisine.png)

![availability result](assets/availability.png)