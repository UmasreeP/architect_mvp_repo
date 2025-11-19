import os, json, requests, textwrap, sys

# ---------- CONFIG ----------
# Set these environment variables or replace with values (not recommended to hardcode)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g. https://openai-demo-architect-agent.openai.azure.com
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")            # Your key (keep secret)
DEPLOYMENT_NAME = os.getenv("AZURE_OAI_DEPLOYMENT", "gpt-4o-demo")  # your deployment name

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    print("ERROR: Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables.")
    sys.exit(1)

# ---------- LOAD INPUT FILES ----------
def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

repo_summary = load_text("repo_summary.txt")
test_report = load_text("repo_issues.json")

# ---------- PROMPT (optimized) ----------
prompt_template = textwrap.dedent("""
SYSTEM: You are "Astra", an AI Test Architect assistant. Answer concisely and strictly follow the requested JSON schema.

USER: 
You will be given:
1) A short repository summary (plain text)
2) A JSON test report

Task:
- Analyze the inputs and return ONLY a JSON object with EXACTLY these fields:
  - overall_score: integer 0-100 (test health)
  - key_findings: array of up to 6 strings (<=120 chars each)
  - top_priorities: array of exactly 3 objects, each:
      {{ "title": string, "impact": "low"|"medium"|"high", "effort_mins": integer, "rationale": string }}
  - simulated_pr_title: short string (<=80 chars)
  - suggested_pr_changes: array of up to 6 short strings (<=120 chars)

Important:
- Return valid JSON only. Do NOT include comments or extraneous text.
- Keep values concise. Use deterministic style. Use "impact" exactly as low/medium/high.

Inputs:
REPO_SUMMARY:
{repo_summary}

TEST_REPORT:
{test_report}
""").format(repo_summary=repo_summary, test_report=test_report)

# ---------- API CALL ----------
url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2023-10-01-preview"

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_KEY
}

body = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_template}
    ],
    "temperature": 0.0,
    "max_tokens": 800
}

print("Sending request to:", url)
resp = requests.post(url, headers=headers, json=body, timeout=120)
resp.raise_for_status()
result = resp.json()

# ---------- PARSE & PRINT ----------
raw = result["choices"][0]["message"]["content"]
print("\n--- RAW MODEL OUTPUT ---\n")
print(raw)

# Try to parse as JSON
try:
    parsed = json.loads(raw)
    print("\n--- PARSED JSON ---\n")
    print(json.dumps(parsed, indent=2))
except Exception as e:
    print("\nERROR: Model output was not valid JSON. Raw output above.")
    print("Exception:", e)
