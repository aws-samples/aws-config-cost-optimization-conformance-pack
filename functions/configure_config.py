import json

import boto3
import cfnresponse

cfg = boto3.client("config")


def get_configuration_recorder():
    configuration_recorders = cfg.describe_configuration_recorders()[
        "ConfigurationRecorders"
    ]
    if configuration_recorders:
        return configuration_recorders[0]
    else:
        raise ValueError(
            "AWS Config is not configured as required. Please review AWS Config to be sure is it is set up in this account and region."
        )


def put_configuration_recorder(name, recording_group, role_arn):
    cfg.put_configuration_recorder(
        ConfigurationRecorder={
            "name": name,
            "recordingGroup": recording_group,
            "roleARN": role_arn,
        }
    )


def handler(event, context):
    # pylint: disable=unused-argument
    print(json.dumps(event))
    try:
        configuration_recorder = get_configuration_recorder()
        if event["RequestType"] in ["Create", "Update"]:
            put_configuration_recorder(
                configuration_recorder["name"],
                configuration_recorder["recordingGroup"],
                event["ResourceProperties"]["ConfigRoleArn"],
            )
            cfnresponse.send(
                event,
                context,
                cfnresponse.SUCCESS,
                None,
                configuration_recorder["roleARN"]
                if event["RequestType"] == "Create"
                else event["PhysicalResourceId"],
            )
        elif event["RequestType"] == "Delete":
            if event["PhysicalResourceId"].startswith("arn:aws:iam"):
                put_configuration_recorder(
                    configuration_recorder["name"],
                    configuration_recorder["recordingGroup"],
                    event["PhysicalResourceId"],
                )
            cfnresponse.send(
                event, context, cfnresponse.SUCCESS, None, event["PhysicalResourceId"]
            )
    except Exception:
        cfnresponse.send(event, context, cfnresponse.FAILED, None, "Config")
        raise
