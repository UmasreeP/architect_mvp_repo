"""
repo_scanner.py
Scans a Playwright repo and generates:
 - repo_summary.txt (human readable)
 - repo_issues.json  (structured issues for the agent)

Usage:
  python repo_scanner.py --repo ./architect_mvp_repo

Outputs:
  ./architect_mvp_repo/repo_summary.txt
  ./architect_mvp_repo/repo_issues.json
"""

import os
import re
import json
import argparse
from collections import defaultdict

# patterns to detect anti-patterns / flaky signals
PATTERNS = {
    "waitForTimeout": r"\bwaitForTimeout\(",
    "hard_sleep": r"\b(page|browser)\.waitForTimeout\(",
    "page_dollar": r"\bpage\.\$\(.*\)",
    "page_click_with_timeout": r"\bpage\.click\([^\)]*,\s*\{[^\}]*timeout",
    "hard_coded_selectors": r"['\"#\.][A-Za-z0-9_\-\[\]\=\'\" >]+['\"]",  # wide match - filtered later
    "expect_assert": r"\bexpect\(",
    "duplicate_login": r"login\(|LoginPage",
    # add more heuristics as needed
}

# helper to read file
def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def scan_repo(repo_path):
    result = {
        "repo_name": os.path.basename(os.path.abspath(repo_path)),
        "total_files": 0,
        "test_files": [],
        "pages_files": [],
        "pattern_counts": defaultdict(int),
        "pattern_examples": defaultdict(list),
        "duplicate_login_files": [],
        "suspicious_selectors_files": [],
        "long_tests_guess": [],  # by heuristics or from report
    }

    for root, dirs, files in os.walk(repo_path):
        # skip node_modules, .git
        if "node_modules" in root or ".git" in root:
            continue
        for fname in files:
            result["total_files"] += 1
            fpath = os.path.join(root, fname)
            low = fname.lower()
            if low.endswith((".spec.ts", ".spec.js", ".test.ts", ".test.js")) or "/tests/" in root.replace("\\","/"):
                result["test_files"].append(os.path.relpath(fpath, repo_path))
            if "/pages/" in root.replace("\\","/") or low.endswith(("page.ts","page.js")):
                result["pages_files"].append(os.path.relpath(fpath, repo_path))

            content = read_text(fpath)
            # find patterns
            for key, pat in PATTERNS.items():
                for m in re.finditer(pat, content):
                    result["pattern_counts"][key] += 1
                    # save up to 3 examples per pattern
                    if len(result["pattern_examples"][key]) < 3:
                        # capture surrounding line
                        line = content[max(0, m.start()-80):m.end()+80].splitlines()[0]
                        result["pattern_examples"][key].append({
                            "file": os.path.relpath(fpath, repo_path),
                            "snippet": line.strip()[:300]
                        })

            # heuristics for duplicate login: count occurrences of "login(" or "LoginPage"
            if re.search(PATTERNS["duplicate_login"], content):
                result["duplicate_login_files"].append(os.path.relpath(fpath, repo_path))

            # suspicious selectors heuristics: presence of '#', '[', ']' or expensive selectors combined with page.$
            if re.search(r"page\.\$\(('#|\"#|\"\.|'\.)", content) or re.search(r"\\[\\]|\\#", content):
                result["suspicious_selectors_files"].append(os.path.relpath(fpath, repo_path))

    # remove duplicates in lists
    result["test_files"] = sorted(list(set(result["test_files"])))
    result["pages_files"] = sorted(list(set(result["pages_files"])))
    result["duplicate_login_files"] = sorted(list(set(result["duplicate_login_files"])))
    result["suspicious_selectors_files"] = sorted(list(set(result["suspicious_selectors_files"])))

    # Summary short text
    summary_lines = []
    summary_lines.append(f"Repo: {result['repo_name']}")
    summary_lines.append(f"Total files scanned: {result['total_files']}")
    summary_lines.append(f"Test files found: {len(result['test_files'])}")
    summary_lines.append(f"Pages / POM files: {len(result['pages_files'])}")
    summary_lines.append("")  # blank line

    # pattern counts
    for k, v in result["pattern_counts"].items():
        if v:
            pretty = k.replace("_", " ")
            summary_lines.append(f"- {pretty}: {v} occurrences")

    # highlight duplicate login and suspicious selectors
    if result["duplicate_login_files"]:
        summary_lines.append(f"- duplicate/inline login found in {len(result['duplicate_login_files'])} files (consider extracting fixture)")
    if result["suspicious_selectors_files"]:
        summary_lines.append(f"- suspicious/unstable selectors found in {len(result['suspicious_selectors_files'])} files")

    # quick recommendation lines
    recs = []
    if result["pattern_counts"].get("waitForTimeout", 0) > 0:
        recs.append("Replace hard waits (waitForTimeout) with explicit waits (waitForSelector/waitForResponse).")
    if result["duplicate_login_files"]:
        recs.append("Extract login flow into a fixture/shared helper to reduce duplication.")
    if result["suspicious_selectors_files"]:
        recs.append("Review selectors for stability (avoid brittle CSS/XPath).")
    if result["pattern_counts"].get("page_dollar", 0) > 0:
        recs.append("Avoid page.$ usage for core actions; use robust waitForSelector or built-in locators.")

    if recs:
        summary_lines.append("")
        summary_lines.append("Quick suggestions:")
        for r in recs:
            summary_lines.append(f"- {r}")

    result["repo_summary_text"] = "\n".join(summary_lines)
    return result

def write_outputs(repo_path, result):
    summary_path = os.path.join(repo_path, "repo_summary.txt")
    issues_path = os.path.join(repo_path, "repo_issues.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(result["repo_summary_text"])
    with open(issues_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {issues_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=False, default=".", help="path to repo root")
    args = parser.parse_args()
    repo_path = args.repo
    print(f"Scanning repo: {repo_path}")
    result = scan_repo(repo_path)
    write_outputs(repo_path, result)

if __name__ == "__main__":
    main()
