def evaluate_compliance(configuration_item, valid_rule_parameters):
    if configuration_item["resourceType"] != "AWS::EC2::Instance":
        return "NOT_APPLICABLE"

    # pylint: disable=undefined-variable
    # boto3 library is already imported in Lambda code.
    recommendations = boto3.client("ce").get_rightsizing_recommendation(
        Configuration={
            "RecommendationTarget": "CROSS_INSTANCE_FAMILY",
            "BenefitsConsidered": True,
        },
        Service="AmazonEC2",
    )
    target_instances = [
        r["ModifyRecommendationDetail"]["TargetInstances"]
        for r in recommendations["RightsizingRecommendations"]
        if r["CurrentInstance"]["ResourceId"] == configuration_item["resourceId"]
    ]
    if len(target_instances) > 0:
        for s in target_instances[0]:
            if (
                "EstimatedMonthlySavings" in s
                and float(s["EstimatedMonthlySavings"]) > 0
            ):
                return "NON_COMPLIANT"

    return "COMPLIANT"
