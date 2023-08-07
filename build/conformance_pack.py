import glob

from cfn_tools import dump_yaml, load_yaml

rules_folder = "rules"
rule_name_prefix = "CostOpt"
parameter_name = "CustomConfigFunctionArn"
output_path = "conformancepack-build.yaml"

template = {
    "Parameters": {parameter_name: {"Type": "String"}},
    "Resources": {},
}

files = glob.glob(f"{rules_folder}/[!_sample]**/resources.yaml", recursive=True)
for function_file in files:
    rule_name = function_file.split("/")[-2]
    resource_content = load_yaml(open(function_file, "r", encoding="utf-8").read())
    resources = list(resource_content["Resources"].keys())
    for resource in resources:
        resource_content["Resources"][resource]["Properties"][
            "ConfigRuleName"
        ] = f"{rule_name_prefix}-{rule_name}"
        if resource_content["Resources"][resource]["Type"] == "AWS::Config::ConfigRule":
            resource_content["Resources"][resource]["Properties"]["Source"][
                "SourceIdentifier"
            ] = {"Ref": parameter_name}
            if (
                "InputParameters"
                in resource_content["Resources"][resource]["Properties"]
            ):
                resource_content["Resources"][resource]["Properties"][
                    "InputParameters"
                ]["customFunctionPrefix"] = rule_name.replace("-", "_").lower()
            else:
                resource_content["Resources"][resource]["Properties"][
                    "InputParameters"
                ] = {"customFunctionPrefix": rule_name.replace("-", "_").lower()}
        elif (
            resource_content["Resources"][resource]["Type"]
            == "AWS::Config::RemediationConfiguration"
        ):
            template["Parameters"][f"{rule_name.replace('-', '')}DocumentArn"] = {
                "Type": "String"
            }
            resource_content["Resources"][resource]["Properties"]["TargetId"] = {
                "Ref": f"{rule_name.replace('-', '')}DocumentArn"
            }
        resource_content["Resources"][
            f"{rule_name.replace('-', '')}{resource}"
        ] = resource_content["Resources"].pop(resource)
    template["Resources"] = {**template["Resources"], **resource_content["Resources"]}

open(output_path, "w", encoding="utf-8").write(dump_yaml(template))
