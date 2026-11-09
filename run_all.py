import subprocess
import sys

for script in ["pipeline.py", "brief.py"]:
    print(f"--- Running {script} ---")
    subprocess.run([sys.executable, script], check=True)