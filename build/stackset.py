import glob

from cfn_tools import dump_yaml, load_yaml

rules_folder = "rules"
template_path = "stackset.yaml"

template_content = load_yaml(open(template_path, "r", encoding="utf-8"))

files = glob.glob(f"{rules_folder}/[!_sample]**/policy.yml", recursive=True)
for function_file in files:
    policy_name = function_file.split("/")[-2].replace("-", "")
    policy_content = load_yaml(open(function_file, "r", encoding="utf-8").read())
    template_content["Resources"]["CustomConfigFunctionRole"]["Properties"][
        "Policies"
    ].append({"PolicyName": policy_name, "PolicyDocument": policy_content})

new_content = dump_yaml(template_content)
new_content = new_content.replace("Fn::Rain::Embed:", "!Rain::Embed")
new_content = new_content.replace("Fn::Rain::Include:", "!Rain::Include")

open(template_path.replace(".yaml", "-build.yaml"), "w", encoding="utf-8").write(
    new_content
)
