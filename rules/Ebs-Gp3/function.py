def evaluate_compliance(configuration_item, valid_rule_parameters):
    if configuration_item["resourceType"] != "AWS::EC2::Volume" or (
        configuration_item["configuration"]["volumeType"] != "gp2"
    ):
        return "NOT_APPLICABLE"

    if (
        configuration_item["configuration"]["volumeType"]
        == valid_rule_parameters["desiredvolumeType"]
    ):
        return "COMPLIANT"

    return "NON_COMPLIANT"
