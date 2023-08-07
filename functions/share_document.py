import json

import boto3
import cfnresponse

ssm = boto3.client("ssm")


def get_accounts(context):
    aws_account_id = context.invoked_function_arn.split(":")[4]
    org = boto3.client("organizations")
    list_accounts = org.list_accounts()
    accountids = [a["Id"] for a in list_accounts["Accounts"] if a["Status"] == "ACTIVE"]
    while "NextToken" in list_accounts:
        list_accounts = org.list_accounts(NextToken=list_accounts["NextToken"])
        accountids += [
            a["Id"] for a in list_accounts["Accounts"] if a["Status"] == "ACTIVE"
        ]
    accountids.remove(aws_account_id)
    return accountids


def share(context, document_name):
    accounts = get_accounts(context)
    for batch in range(0, len(accounts), 20):
        ssm.modify_document_permission(
            Name=document_name,
            PermissionType="Share",
            AccountIdsToAdd=accounts[batch : batch + 20],
        )


def unshare(context, document_name):
    accounts = get_accounts(context)
    for batch in range(0, len(accounts), 20):
        ssm.modify_document_permission(
            Name=document_name,
            PermissionType="Share",
            AccountIdsToRemove=accounts[batch : batch + 20],
        )


def handler(event, context):
    print(json.dumps(event))
    try:
        if event["RequestType"] == "Create":
            share(context, event["ResourceProperties"]["DocumentName"])
        elif event["RequestType"] == "Update":
            unshare(context, event["OldResourceProperties"]["DocumentName"])
            share(context, event["ResourceProperties"]["DocumentName"])
        elif event["RequestType"] == "Delete":
            unshare(context, event["ResourceProperties"]["DocumentName"])
        cfnresponse.send(event, context, cfnresponse.SUCCESS, None, "ShareDocument")
    except Exception:
        cfnresponse.send(event, context, cfnresponse.FAILED, None, "ShareDocument")
        raise
