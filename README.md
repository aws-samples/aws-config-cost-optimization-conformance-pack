# hmb-412-CostOptimizationConformance

This repository contains code to deploy the Cost Optimization Orgnaization Conformance pack into an AWS Organization.

## Pre-requisites

In order to use this solution the following components must be already deployed within an AWS account.

- AWS Organizations.
- AWS Config deployed in same region in all member accounts of the AWS Organization.
- Delegated AWS Config account within AWS Organizations.
- Delegated AWS CloudFormation Stackets account within AWS Organizations.

## Deployment guide

Create a new CloudFormation stack using the `main.yaml` file
