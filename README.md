# Cost Optimization Conformance

This repository contains code to deploy the Cost Optimization Organization Conformance pack into an AWS Organization.

## Pre-requisites

To use this solution, the following components must be already deployed within an AWS account.

- AWS Organizations.
- AWS Config deployed in same region in all member accounts of the AWS Organization.
- Delegated AWS Config account within AWS Organizations.
- Delegated AWS CloudFormation Stackets account within AWS Organizations.

## Deployment Guide

Download `template.yaml` from the latest release.

Create a new CloudFormation stack using this `template.yaml` file.
