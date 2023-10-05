def evaluate_compliance(configuration_item, valid_rule_parameters):
    try:
        s3 = boto3.client("s3")  # pylint: disable=undefined-variable
        lifecycle_configuration = s3.get_bucket_lifecycle_configuration(
            Bucket=configuration_item["resourceName"]
        )
        if (
            "Rules" not in lifecycle_configuration
            or len(lifecycle_configuration["Rules"]) == 0
        ):
            return "NON_COMPLIANT"
        return "COMPLIANT"
    except botocore.exceptions.ClientError as ex:  # pylint: disable=undefined-variable
        if "NoSuchLifecycleConfiguration" in ex.response["Error"]["Code"]:
            return "NON_COMPLIANT"
        else:
            raise ex
