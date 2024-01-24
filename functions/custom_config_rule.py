import datetime
import json

import boto3

AWS_CONFIG_CLIENT = boto3.client("config")


def evaluate_compliance(configuration_item, rule_parameters):
    # pylint: disable=unused-argument
    rule_eval = globals()[
        f"{rule_parameters['customFunctionPrefix']}_evaluate_compliance"
    ]
    return rule_eval(configuration_item, rule_parameters)


def check_defined(reference, reference_name):
    if not reference:
        # pylint: disable=broad-exception-raised
        raise Exception("Error: ", reference_name, "is not defined")
    return reference


def is_oversized_changed_notification(message_type):
    check_defined(message_type, "messageType")
    return message_type == "OversizedConfigurationItemChangeNotification"


def get_configuration(resource_type, resource_id, configuration_capture_time=None):
    request = {
        "resourceType": resource_type,
        "resourceId": resource_id,
        "limit": 1,
    }
    if configuration_capture_time:
        request["laterTime"] = (configuration_capture_time,)
    result = AWS_CONFIG_CLIENT.get_resource_config_history(**request)
    configuration_item = result["configurationItems"][0]
    return convert_api_configuration(configuration_item)


def convert_api_configuration(configuration_item):
    for k, v in configuration_item.items():
        if isinstance(v, datetime.datetime):
            configuration_item[k] = str(v)
    configuration_item["awsAccountId"] = configuration_item["accountId"]
    configuration_item["ARN"] = configuration_item["arn"]
    configuration_item["configurationStateMd5Hash"] = configuration_item[
        "configurationItemMD5Hash"
    ]
    configuration_item["configurationItemVersion"] = configuration_item["version"]
    configuration_item["configuration"] = json.loads(
        configuration_item["configuration"]
    )
    if "relationships" in configuration_item:
        for i in range(len(configuration_item["relationships"])):
            configuration_item["relationships"][i]["name"] = configuration_item[
                "relationships"
            ][i]["relationshipName"]
    return configuration_item


def get_configuration_item(invoking_event):
    check_defined(invoking_event, "invokingEvent")
    if is_oversized_changed_notification(invoking_event["messageType"]):
        configuration_item_summary = check_defined(
            invoking_event["configurationItemSummary"], "configurationItemSummary"
        )
        return get_configuration(
            configuration_item_summary["resourceType"],
            configuration_item_summary["resourceId"],
            configuration_item_summary["configurationItemCaptureTime"],
        )
    return check_defined(invoking_event["configurationItem"], "configurationItem")


def is_applicable(configuration_item, event):
    try:
        check_defined(configuration_item, "configurationItem")
        check_defined(event, "event")
    # pylint: disable=bare-except
    except:
        return True
    status = configuration_item["configurationItemStatus"]
    event_left_scope = event["eventLeftScope"]
    if status == "ResourceDeleted":
        print("Resource Deleted, setting Compliance Status to NOT_APPLICABLE.")

    return status in ("OK", "ResourceDiscovered") and not event_left_scope


def build_evaluation(configuration_item, event, rule_parameters):
    compliance_value = "NOT_APPLICABLE"
    if is_applicable(configuration_item, event):
        compliance_value = evaluate_compliance(configuration_item, rule_parameters)

    return {
        "ComplianceResourceType": configuration_item["resourceType"],
        "ComplianceResourceId": configuration_item["resourceId"],
        "ComplianceType": compliance_value,
        "OrderingTimestamp": configuration_item["configurationItemCaptureTime"],
    }


def evaluate_parameters(rule_parameters):
    if "applicableResourceType" not in rule_parameters:
        raise ValueError(
            'The parameter with "applicableResourceType" as key must be defined.'
        )
    if not rule_parameters["applicableResourceType"]:
        raise ValueError(
            'The parameter "applicableResourceType" must have a defined value.'
        )
    return rule_parameters


def get_configuration_items(resource_type):
    resource_keys = list_discovered_resources(resource_type)
    resource_configs = batch_get_resource_config(resource_keys)
    configuration_items = []
    for rc in resource_configs:
        configuration_items.append(
            get_configuration(
                rc["resourceType"],
                rc["resourceId"],
            )
        )
    return configuration_items


def list_discovered_resources(resource_type):
    response = AWS_CONFIG_CLIENT.list_discovered_resources(resourceType=resource_type)
    resources = [
        {"resourceType": r["resourceType"], "resourceId": r["resourceId"]}
        for r in response["resourceIdentifiers"]
    ]
    while "nextToken" in response:
        response = AWS_CONFIG_CLIENT.list_discovered_resources(
            resourceType=resource_type, nextToken=response["nextToken"]
        )
        resources.extend(
            [
                {"resourceType": r["resourceType"], "resourceId": r["resourceId"]}
                for r in response["resourceIdentifiers"]
            ]
        )
    return resources


def batch_get_resource_config(resource_keys):
    if len(resource_keys) == 0:
        return []
    response = AWS_CONFIG_CLIENT.batch_get_resource_config(resourceKeys=resource_keys)
    resources = [
        {
            "resourceType": r["resourceType"],
            "resourceId": r["resourceId"],
            "configurationItemCaptureTime": r["configurationItemCaptureTime"],
        }
        for r in response["baseConfigurationItems"]
    ]
    while len(response["unprocessedResourceKeys"]) > 0:
        response = AWS_CONFIG_CLIENT.batch_get_resource_config(
            resourceKeys=response["unprocessedResourceKeys"]
        )
        resources.extend(
            [
                {
                    "resourceType": r["resourceType"],
                    "resourceId": r["resourceId"],
                    "configurationItemCaptureTime": r["configurationItemCaptureTime"],
                }
                for r in response["baseConfigurationItems"]
            ]
        )
    return resources


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    check_defined(event, "event")
    invoking_event = json.loads(event["invokingEvent"])
    rule_parameters = (
        json.loads(event["ruleParameters"]) if "ruleParameters" in event else {}
    )
    match invoking_event["messageType"]:
        case "ScheduledNotification":
            valid_rule_parameters = evaluate_parameters(rule_parameters)
            evaluations = [
                build_evaluation(
                    configuration_item,
                    event,
                    valid_rule_parameters,
                )
                for configuration_item in get_configuration_items(
                    valid_rule_parameters["applicableResourceType"]
                )
            ]
        case "ConfigurationItemChangeNotification" | "OversizedConfigurationItemChangeNotification":
            configuration_item = get_configuration_item(invoking_event)
            evaluations = [
                build_evaluation(
                    configuration_item,
                    event,
                    rule_parameters,
                ),
            ]
        case _:
            return build_internal_error_response(
                "Unexpected message type", str(invoking_event)
            )
    AWS_CONFIG_CLIENT.put_evaluations(
        Evaluations=evaluations,
        ResultToken=event["resultToken"],
    )


def build_internal_error_response(internal_error_message, internal_error_details=None):
    return build_error_response(
        internal_error_message, internal_error_details, "InternalError", "InternalError"
    )


def build_error_response(
    internal_error_message,
    internal_error_details=None,
    customer_error_code=None,
    customer_error_message=None,
):
    error_response = {
        "internalErrorMessage": internal_error_message,
        "internalErrorDetails": internal_error_details,
        "customerErrorMessage": customer_error_message,
        "customerErrorCode": customer_error_code,
    }
    print(error_response)
    return error_response
