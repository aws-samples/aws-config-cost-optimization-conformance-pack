import glob

from cfn_tools import dump_yaml, load_yaml

rules_folder = "rules"
template_path = "template.yaml"

template_content = load_yaml(open(template_path, "r", encoding="utf-8"))

files = glob.glob(f"{rules_folder}/[!_sample]**/policy.yml", recursive=True)
for function_file in files:
    policy_name = function_file.split("/")[-2].replace("-", "")
    policy_content = load_yaml(open(function_file, "r", encoding="utf-8").read())
    template_content["Resources"]["CustomConfigFunction"]["Properties"][
        "Policies"
    ].append(policy_content)

files = glob.glob(f"{rules_folder}/[!_sample]**/remediation.yml", recursive=True)
for function_file in files:
    resource_prefix = function_file.split("/")[-2].replace("-", "")
    template_content["Resources"][f"{resource_prefix}Remediation"] = {
        "Type": "AWS::SSM::Document",
        "Properties": {
            "DocumentType": "Automation",
            "DocumentFormat": "YAML",
            "Content": {"Fn::Rain::Include": function_file},
        },
    }
    template_content["Resources"][f"{resource_prefix}RemediationShare"] = {
        "Type": "Custom::ShareDocument",
        "Properties": {
            "ServiceToken": {"Fn::GetAtt": ["ShareDocumentFunction", "Arn"]},
            "DocumentName": {"Ref": f"{resource_prefix}Remediation"},
        },
    }
    template_content["Resources"]["ConformancePack"]["Properties"][
        "ConformancePackInputParameters"
    ].append(
        {
            "ParameterName": f"{resource_prefix}DocumentArn",
            "ParameterValue": {
                "Fn::Sub": f"arn:${{AWS::Partition}}:ssm:${{AWS::Region}}:${{AWS::AccountId}}:document/${{{resource_prefix}Remediation}}"
            },
        }
    )

new_content = dump_yaml(template_content)
new_content = new_content.replace("Fn::Rain::Embed:", "!Rain::Embed")
new_content = new_content.replace("Fn::Rain::Include:", "!Rain::Include")

open(template_path.replace(".yaml", "-build.yaml"), "w", encoding="utf-8").write(
    new_content
)
