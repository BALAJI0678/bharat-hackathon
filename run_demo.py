"""Run synthetic evidence only; do not bypass human report approval."""
import json
from pathlib import Path
from agent import parse_evidence, run_agent, verify_audit

root = Path(__file__).resolve().parent
raw = (root / "samples/bharat-demo.json").read_text(encoding="utf-8")
records, warnings = parse_evidence(raw, "bharat-demo.json")
run = run_agent(records, "Review fraud and payment indicators", warnings)
assert verify_audit(run["audit"])
out = root / "outputs"
out.mkdir(exist_ok=True)
(out / "review-packet.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
lines = ["# Synthetic agent execution", "", "**Status: awaiting human review — not an approved report.**", "", run["summary"], "", "## Execution trace"]
for event in run["audit"]:
    lines.append(f"- {event['sequence']}. **{event['stage']}** / `{event['tool']}`: {event['decision']}")
lines += ["", "## Findings"]
for f in run["findings"]:
    lines += [f"### {f['id']}: {f['title']}", "Evidence: " + ", ".join(f["evidence_ids"]), f["reasoning"], ""]
lines += ["## Warnings"] + ["- " + w for w in run["warnings"]]
(out / "execution.md").write_text("\n".join(lines), encoding="utf-8")
print(run["summary"])
print("Status:", run["status"])
print("Audit verified:", verify_audit(run["audit"]))
