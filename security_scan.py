#!/usr/bin/env python3

import subprocess
import shutil
import os
import sys

# Folder for all scan reports
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# Target URL for DAST tools
TARGET_URL = os.environ.get("TARGET_URL", "http://localhost:3000")
JAVA_PROJECT_DIR = os.environ.get("JAVA_PROJECT_DIR", "./")

# List of tools to check
TOOLS = {
    "semgrep": ["semgrep", "--version"],
    "spotbugs": ["spotbugs", "-version"],
    "zap": ["zap.sh", "-version"],
    "sqlmap": ["sqlmap", "--version"]
}


def banner(msg):
    print("\n" + "="*60)
    print(msg)
    print("="*60)


def check_tool(tool, command):
    """Check if a tool is installed and runnable."""
    print(f"[+] Checking {tool}...")
    if shutil.which(command[0]) is None:
        print(f"[✗] {tool} is NOT installed. Skipping.")
        return False
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[✓] {tool} is installed")
        return True
    except Exception:
        print(f"[✗] {tool} is installed but failed to run")
        return False


def run_semgrep():
    """Run Semgrep SAST scan."""
    if not check_tool("semgrep", TOOLS["semgrep"]):
        return
    banner("Running Semgrep (SAST)")
    output_file = os.path.join(REPORT_DIR, "semgrep.json")
    cmd = [
        "semgrep",
        "--config=auto",
        "--json",
        "--output", output_file
    ]
    subprocess.run(cmd, check=False)
    print(f"[✓] Semgrep report saved to {output_file}")


def run_spotbugs():
    """Run SpotBugs on Java project."""
    if not check_tool("spotbugs", TOOLS["spotbugs"]):
        return
    banner("Running SpotBugs (Java SAST)")
    output_file = os.path.join(REPORT_DIR, "spotbugs.xml")
    if not os.path.exists(JAVA_PROJECT_DIR):
        print("[!] Java project directory not found. Skipping SpotBugs.")
        return
    cmd = [
        "spotbugs",
        "-textui",
        "-effort:max",
        "-low",
        "-xml:withMessages",
        "-output", output_file,
        JAVA_PROJECT_DIR
    ]
    subprocess.run(cmd, check=False)
    print(f"[✓] SpotBugs report saved to {output_file}")


def run_zap():
    """Run OWASP ZAP DAST scan."""
    if not check_tool("zap", TOOLS["zap"]):
        return
    banner("Running OWASP ZAP (DAST)")
    output_file = os.path.join(REPORT_DIR, "zap_report.html")
    cmd = [
        "zap.sh",
        "-cmd",
        "-quickurl", TARGET_URL,
        "-quickprogress",
        "-quickout", output_file
    ]
    subprocess.run(cmd, check=False)
    print(f"[✓] ZAP report saved to {output_file}")


def run_sqlmap():
    """Run SQLMap against target URL."""
    if not check_tool("sqlmap", TOOLS["sqlmap"]):
        return
    banner("Running SQLMap (DAST)")
    sqlmap_dir = os.path.join(REPORT_DIR, "sqlmap")
    os.makedirs(sqlmap_dir, exist_ok=True)
    cmd = [
        "sqlmap",
        "-u", f"{TARGET_URL}/login",
        "--batch",
        "--crawl=1",
        "--output-dir", sqlmap_dir
    ]
    subprocess.run(cmd, check=False)
    print(f"[✓] SQLMap report saved to {sqlmap_dir}")


def main():
    banner("Starting Security Scan")
    run_semgrep()
    run_spotbugs()
    run_zap()
    run_sqlmap()
    banner("Security Scan Completed")
    print(f"[✓] All reports saved in ./{REPORT_DIR}")


if __name__ == "__main__":
    main()
