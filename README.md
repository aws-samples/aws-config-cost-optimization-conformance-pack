# Optimizing AWS Resource Costs using AWS Config

This repository contains code to deploy the Cost Optimization Conformance Pack solution across an AWS Organization that utilises Control Tower. It includes an example collection of three custom rules containing best practice cost optimization logic. These will monitor and evaluate your resources to identify their cost optimization compliance posture and consolidate the results back to a single ‘delegated administrator’ account for simplified management. The following rules are included:

Rule 1: Check for EBS gp2 volumes Remediation: Convert them to gp3 volumes 
Rule 2: Check for EBS volumes not attached to an EC2 instance
Rule 3: Check for S3 buckets that do not have a lifecycle configuration policy 

For this solution the following will be deployed:

- **AWS Config Organization Conformance Pack** - a collection of AWS Config custom rules that will be used to evaluate resources against best practice cost optimization logic. 
  - This Organization Conformance Pack will deploy individual Cost Optimization Conformance Packs into each member account.
- **AWS CloudFormation StackSet** - a collection of CloudFormation stacks deployed into all the member accounts in the AWS Organization. These stacks will deploy the following:
  - **AWS Lambda Function** - The AWS Config custom rules invoke a Lambda function that contains the logic to evaluate whether the specified resource is either Compliant or Noncompliant with cost optimization best practice rules defined above.
  - **IAM Roles** - Two custom IAM roles will be deployed. One that will enable the Lambda function to be invoked and the second which will be used by AWS Systems Manager (SSM) to carry out remediation actions as defined in the SSM document.
- **AWS Systems Manager Automation Document** - This will be deployed into the audit account only and used by the member accounts.


## Pre-requisites

To use this solution you will need the following:

- AWS Organizations utilising AWS Control Tower
- Permission to access both your organizations management account and the audit account you are delegating administrative rights to for deployment of the Cost Optimization Conformance Pack solution.
- Trusted access for StackSets with AWS Organizations enabled.
- AWS Console access to AWS Config in the member accounts where the solution is being deployed 

## Walkthrough

In this solution walkthrough you will complete the following steps:

- Establish a trust relationship between AWS Organizations and the service principals for AWS Config and AWS CloudFormation StackSets
- Grant *delegated administrator* permissions for the AWS Config and AWS CloudFormation services to the audit account
- Deploy the Cost Optimization Conformance Pack 
- Using CloudFormation, you will deploy the conformance pack, Lambda function, IAM roles and Systems Manager document included in the solution 
- Test the solution 

## Deployment

For the purposes of this deployment walkthrough, our management account ID will be 111111111111 and the audit account from which we will deploy the solution will have an account ID of 222222222222

**Establish a trust relationship between AWS Organizations and the service principals for AWS Config and AWS CloudFormation**

1. Run the following commands using the AWS CLI or an AWS CloudShell session
    - `aws organizations enable-aws-service-access --service-principal=config-multiaccountsetup.amazonaws.com`
    - `aws organizations enable-aws-service-access --service-principal=member.org.stacksets.cloudformation.amazonaws.com`
2. Validate they have been successful by running the command `aws organizations list-aws-service-access-for-organization` where they will be listed as service principals

**Setup a delegated administrator account for AWS Config and AWS CloudFormation**

1. Run the following CLI commands replacing the account-id with the ID of your audit account:
    - `aws organizations register-delegated-administrator --account-id 222222222222 --service-principal config-multiaccountsetup.amazonaws.com`
    - `aws organizations register-delegated-administrator --account-id 222222222222 --service-principal config.amazonaws.com`
    - `aws organizations register-delegated-administrator  --service-principal=member.org.stacksets.cloudformation.amazonaws.com  --account-id=222222222222`
2. Validate they have been successful by running the following commands where you should see the listed delegated administrators:
    - `aws organizations list-delegated-administrators --service-principal=config.amazonaws.com`
    - `aws organizations list-delegated-administrators --service-principal=config-multiaccountsetup.amazonaws.com`
    - `aws organizations list-delegated-administrators  --service-principal=member.org.stacksets.cloudformation.amazonaws.com`

**Deploy the Cost Optimization Conformance Pack**

1. Download `template.yaml` from the latest release.
2. Using AWS CLI or an AWS CloudShell sesssion, create a new CloudFormation stack with the following command that refers to the `template.yaml` file:   
    - `aws cloudformation deploy --template-file template.yaml --stack-name CostOptimizationConfPack --parameter-overrides DeployingInDelegatedAdminAccount=True --capabilities CAPABILITY_IAM `
3. You can verify the resources have deployed successfully by navigating to CloudFormation in the AWS Console and selecting Stacks from the menu. 


## Testing

The Cost Optimization Conformation Pack should now be deployed across the Organization and you can view the compliance status of the rules by navigating to the AWS Config dashboard and selecting Conformance packs from the menu.
The rules will automatically evaluate resources in your accounts that match the criteria however, if you do not have any that match you can [create an Amazon EBS volume](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-creating-volume.html) and set the `Volume Type` as `gp2`.  

Once the EBS volume has been created, follow the steps below in the AWS Console to re-evaluate resources in the account:

1.  Navigate to the AWS Config dashboard.
2.	Select ‘Conformance packs’.
3.	Select the conformance pack with **CostOptimization** in the name.
4.	A list of Rules will appear 
5.	Select the rule with **CostOpt-Ebs** in the name to view the rule dashboard.
6.	Select the Actions menu.
7.	Select Re-evaluate to trigger the rule to assess the resources in the account.

After the evaluation has completed the **Noncompliant** EBS volume will display

To invoke the remediation rule follow the steps below in the AWS Console:

1.	From the AWS Config rule dashboard scroll down to **Resources in scope**.
2.	Select the radio button for the EC2 Volume that is listed as **Noncompliant**.
3.	Select the Remediate button.

Once the remediation rule has been triggered Action executed successfully should then appear under the Status column. 
You can also validate the change in volume type has completed successfully by looking at the volumes listed in the Elastic Block Store under the EC2 service. 

## Clean Up

All the resources deployed for the Cost Optimization Conformance Pack solution can be removed by deleting the CloudFormation stack either through the AWS Console, or using the CLI command below: 

To delete the Cost Optimization Conformance Pack solution (CLI)

1.	Using AWS CLI or an AWS CloudShell session run the `aws cloudformation delete-stack --stack-name CostOptimizationConfPack` command. 


## Further Reading

You can find out more about [AWS Config custom Lambda rules](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html) and [AWS Systems Manager documents](https://docs.aws.amazon.com/systems-manager/latest/userguide/documents.html) to expand the functionality of the solution further. 


## Security 

See [CONTRIBUTING](https://github.com/aws-samples/aws-config-cost-optimization-conformance-pack/blob/main/CONTRIBUTING.md) for more information.

## License 

This library is licensed under the MIT-0 License. See the LICENSE file.