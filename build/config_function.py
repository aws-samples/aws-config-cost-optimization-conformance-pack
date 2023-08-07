import glob

rules_folder = "rules"
config_function_path = "functions/custom_config_rule.py"

lambda_content = open(config_function_path, "r", encoding="utf-8").read()

files = glob.glob(f"{rules_folder}/[!_sample]**/function.py", recursive=True)
for function_file in files:
    function_prefix = function_file.split("/")[-2].replace("-", "_").lower()
    function_content = open(function_file, "r", encoding="utf-8").read()
    lambda_content += "\n\n" + function_content.replace(
        "def evaluate_compliance(", f"def {function_prefix}_evaluate_compliance("
    )

open(config_function_path.replace(".py", "-pkg.py"), "w", encoding="utf-8").write(
    lambda_content
)
