import glob

from cfn_tools import dump_yaml, load_yaml

rules_folder = "rules"
rule_name_prefix = "CostOpt"
output_path = "conformancepack-build.yaml"

template = {
    "Parameters": {},
    "Resources": {},
}

files = glob.glob(f"{rules_folder}/[!_sample]**/resources.yaml", recursive=True)
for resource_file in files:
    rule_name = resource_file.split("/")[-2]
    resource_content = load_yaml(open(resource_file, "r", encoding="utf-8").read())
    for logical_id, resource in resource_content["Resources"].items():
        resource["Properties"]["ConfigRuleName"] = f"{rule_name_prefix}-{rule_name}"
        if resource["Type"] == "AWS::Config::ConfigRule":
            resource["Properties"]["Source"]["SourceIdentifier"] = {
                "Fn::Sub": "arn:${AWS::Partition}:lambda:${AWS::Region}:${AWS::AccountId}:function:CostOptimizationConformanceConfigRuleFunction"
            }
            if "InputParameters" in resource["Properties"]:
                resource["Properties"]["InputParameters"][
                    "customFunctionPrefix"
                ] = rule_name.replace("-", "_").lower()
            else:
                resource["Properties"]["InputParameters"] = {
                    "customFunctionPrefix": rule_name.replace("-", "_").lower()
                }
        elif resource["Type"] == "AWS::Config::RemediationConfiguration":
            if "DependsOn" in resource:
                resource[
                    "DependsOn"
                ] = f'{rule_name.replace("-", "")}{resource["DependsOn"]}'
            template["Parameters"][f"{rule_name.replace('-', '')}DocumentArn"] = {
                "Type": "String"
            }
            resource["Properties"]["TargetId"] = {
                "Ref": f"{rule_name.replace('-', '')}DocumentArn"
            }
        resource_content["Resources"][
            f"{rule_name.replace('-', '')}{logical_id}"
        ] = resource_content["Resources"].pop(logical_id)
    template["Resources"] = {**template["Resources"], **resource_content["Resources"]}

open(output_path, "w", encoding="utf-8").write(dump_yaml(template))
