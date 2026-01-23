#!/usr/bin/env python3

import json
import os
import xml.etree.ElementTree as ET

REPORT_DIR = "reports"
OUTPUT_JSON = f"{REPORT_DIR}/high_risk_report.json"
OUTPUT_TXT = f"{REPORT_DIR}/high_risk_report.txt"

high_risks = []


def add_finding(tool, title, severity, location, description):
    high_risks.append({
        "tool": tool,
        "title": title,
        "severity": severity,
        "location": location,
        "description": description
    })


# ---------------- SEMGREP ----------------
def parse_semgrep():
    path = f"{REPORT_DIR}/semgrep.json"
    if not os.path.exists(path):
        return

    with open(path) as f:
        data = json.load(f)

    for result in data.get("results", []):
        severity = result.get("extra", {}).get("severity", "").upper()
        if severity in ["HIGH", "CRITICAL"]:
            add_finding(
                "Semgrep",
                result.get("check_id"),
                severity,
                f"{result.get('path')}:{result.get('start', {}).get('line')}",
                result.get("extra", {}).get("message")
            )


# ---------------- SPOTBUGS ----------------
def parse_spotbugs():
    path = f"{REPORT_DIR}/spotbugs.xml"
    if not os.path.exists(path):
        return

    tree = ET.parse(path)
    root = tree.getroot()

    for bug in root.findall("BugInstance"):
        priority = bug.get("priority")
        if priority == "1":  # High priority
            class_name = bug.find("Class").get("classname")
            add_finding(
                "SpotBugs",
                bug.get("type"),
                "HIGH",
                class_name,
                bug.findtext("LongMessage")
            )


# ---------------- ZAP ----------------
def parse_zap():
    path = f"{REPORT_DIR}/zap.json"
    if not os.path.exists(path):
        return

    with open(path) as f:
        data = json.load(f)

    for site in data.get("site", []):
        for alert in site.get("alerts", []):
            risk = alert.get("riskdesc", "").upper()
            if "HIGH" in risk:
                add_finding(
                    "OWASP ZAP",
                    alert.get("alert"),
                    "HIGH",
                    alert.get("url"),
                    alert.get("desc")
                )


# ---------------- SQLMAP ----------------
def parse_sqlmap():
    sqlmap_dir = f"{REPORT_DIR}/sqlmap"
    if not os.path.exists(sqlmap_dir):
        return

    for root, _, files in os.walk(sqlmap_dir):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if "CRITICAL" in content or "injectable" in content.lower():
                        add_finding(
                            "SQLMap",
                            "SQL Injection",
                            "CRITICAL",
                            file,
                            "SQL injection vulnerability detected"
                        )


def generate_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)

    with open(OUTPUT_JSON, "w") as jf:
        json.dump(high_risks, jf, indent=2)

    with open(OUTPUT_TXT, "w") as tf:
        tf.write("HIGH / CRITICAL SECURITY FINDINGS\n")
        tf.write("=" * 40 + "\n\n")

        for f in high_risks:
            tf.write(f"Tool: {f['tool']}\n")
            tf.write(f"Title: {f['title']}\n")
            tf.write(f"Severity: {f['severity']}\n")
            tf.write(f"Location: {f['location']}\n")
            tf.write(f"Description: {f['description']}\n")
            tf.write("-" * 40 + "\n")

    print(f"[✓] High-risk report generated:")
    print(f"    - {OUTPUT_JSON}")
    print(f"    - {OUTPUT_TXT}")


def main():
    parse_semgrep()
    parse_spotbugs()
    parse_zap()
    parse_sqlmap()
    generate_reports()


if __name__ == "__main__":
    main()
