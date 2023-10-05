def evaluate_compliance(configuration_item, valid_rule_parameters):
    if (
        "attachments" not in configuration_item["configuration"]
        or len(configuration_item["configuration"]["attachments"]) == 0
    ):
        return "NON_COMPLIANT"
    return "COMPLIANT"
