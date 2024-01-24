def evaluate_compliance(configuration_item, valid_rule_parameters):
    if configuration_item["configuration"]["volumeType"] == "gp2":
        return "NON_COMPLIANT"
    if (
        configuration_item["configuration"]["volumeType"]
        == valid_rule_parameters["desiredVolumeType"]
    ):
        return "COMPLIANT"

    return "NOT_APPLICABLE"
