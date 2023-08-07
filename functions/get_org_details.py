import json

import boto3
import cfnresponse

org = boto3.client("organizations")


def handler(event, context):
    # pylint: disable=unused-argument
    print(json.dumps(event))
    try:
        if event["RequestType"] in ["Create", "Update"]:
            response = {
                "MasterAccountId": org.describe_organization()["Organization"][
                    "MasterAccountId"
                ]
            }
            cfnresponse.send(
                event,
                context,
                cfnresponse.SUCCESS,
                response,
                org.list_roots()["Roots"][0]["Id"],
            )
        elif event["RequestType"] == "Delete":
            cfnresponse.send(event, context, cfnresponse.SUCCESS, None, "RootId")
    except Exception:
        cfnresponse.send(event, context, cfnresponse.FAILED, None, "RootId")
        raise
