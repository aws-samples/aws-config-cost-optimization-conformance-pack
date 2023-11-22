import glob

from cfn_tools import dump_yaml, load_yaml

rules_folder = "rules"
template_path = "stackset.yaml"

template_content = load_yaml(open(template_path, "r", encoding="utf-8"))

function_policy_files = glob.glob(
    f"{rules_folder}/[!_sample]**/function_policy.yml", recursive=True
)
for policy_file in function_policy_files:
    policy_name = policy_file.split("/")[-2].replace("-", "")
    policy_content = load_yaml(open(policy_file, "r", encoding="utf-8").read())
    template_content["Resources"]["CustomConfigFunctionRole"]["Properties"][
        "Policies"
    ].append({"PolicyName": policy_name, "PolicyDocument": policy_content})

remediation_policy_files = glob.glob(
    f"{rules_folder}/[!_sample]**/remediation_policy.yml", recursive=True
)
for policy_file in remediation_policy_files:
    policy_name = policy_file.split("/")[-2].replace("-", "")
    policy_content = load_yaml(open(policy_file, "r", encoding="utf-8").read())
    template_content["Resources"]["AutomationRole"]["Properties"]["Policies"].append(
        {"PolicyName": policy_name, "PolicyDocument": policy_content}
    )

new_content = dump_yaml(template_content)
new_content = new_content.replace("Fn::Rain::Embed:", "!Rain::Embed")
new_content = new_content.replace("Fn::Rain::Include:", "!Rain::Include")

open(template_path.replace(".yaml", "-build.yaml"), "w", encoding="utf-8").write(
    new_content
)
