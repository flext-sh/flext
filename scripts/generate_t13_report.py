import os
import re
import json

reports_dir = ".reports/workspace/check"
output_file = ".reports/refactor/t13-semantic-validation.json"

results = {}

for filename in os.listdir(reports_dir):
    if filename.endswith(".log"):
        project = filename[:-4]
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, "r") as f:
            content = f.read()

            match = re.search(
                r"ERROR: " + re.escape(project) + r"\s+(\d+)\s+\((.*?)\)", content
            )
            if match:
                total = int(match.group(1))
                details_str = match.group(2)
                details = {}
                for item in details_str.split(", "):
                    key, val = item.split("=")
                    details[key] = int(val)

                results[project] = {
                    "total": total,
                    "details": details,
                    "status": "FAIL" if total > 0 else "PASS",
                }
            else:
                if "Success: 1" in content or "Success: 5" in content:
                    results[project] = {"total": 0, "details": {}, "status": "PASS"}
                else:
                    results[project] = {"total": -1, "details": {}, "status": "UNKNOWN"}

with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"Report generated: {output_file}")
