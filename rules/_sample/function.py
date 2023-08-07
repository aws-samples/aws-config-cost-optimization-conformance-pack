def evaluate_compliance(configuration_item, valid_rule_parameters):
    """Form the evaluation(s) to be return to Config Rules

    Return either:
    None -- when no result needs to be displayed
    a string -- either COMPLIANT, NON_COMPLIANT or NOT_APPLICABLE

    Keyword arguments:
    configuration_item -- the configurationItem dictionary in the invokingEvent
    valid_rule_parameters -- the validated parameters of the Config Rule

    Additional imports:
    Check the full Lambda function code in the file functions/custom_config_rule.py for all existing imports
    """
