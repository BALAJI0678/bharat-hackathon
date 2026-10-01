# Run Bharat Evidence Agent on GitHub

This repository executes the original deterministic Python agent with synthetic evidence through GitHub Actions. It is not an LLM agent or a hosted web application.

## Exact steps

1. Extract this package.
2. Upload its contents to your repository root, including the hidden `.github` directory. Do not upload only the ZIP or only this Markdown document.
3. Commit to the default branch. The workflow also runs automatically on pushes to `main`.
4. Open **Actions → Run Bharat Evidence Agent → Run workflow**.
5. Open the completed run to view its job summary and logs.
6. Download **synthetic-agent-results** from the run's artifacts for the execution Markdown and JSON review packet.

The manual workflow must be committed to the default branch. Enable GitHub Actions if your repository has it disabled. The workflow uses GitHub-hosted runners; usage is subject to your account's Actions limits.

## What actually runs

```bash
python -m unittest discover -s tests -v
python run_demo.py
```

The script imports the supplied synthetic records, validates their import hashes, builds a timeline, extracts entities, scans communication indicators, conditionally correlates payments, and verifies the audit chain.

Locally verified result: 20 tests passed; 7 records; 3 review leads; 6 timestamped events; 1 missing-timestamp warning. Run IDs, timestamps and audit hashes vary on each execution.

## Human-review boundary

The output remains `awaiting_review`. The workflow does not impersonate a reviewer, approve a report, or use real evidence. The generated Markdown is an execution trace, not the application’s approved report.

To use the interactive review interface locally:

```bash
python server.py
```

Open `http://127.0.0.1:8787`, load the synthetic demo, run the workflow, inspect the evidence, and explicitly approve as a human reviewer before exporting the reviewed report.

GitHub Actions runs a finite demo job; it does not provide a persistent public web UI. No repository has been published by this package. Never commit real evidence, case databases or credentials.

## Team Members
- **Tumma Sevireddy** (ID: 99240040699 | Email: 99240040699@klu.ac.in | Phone: 7671975351)
- **Pallapotu Balaji** (ID: 99240041234 | Email: 99240041234@klu.ac.in | Phone: 9392774307)
- **Daggupati Vinusha** (ID: 99240041217 | Email: 99240041217@klu.ac.in | Phone: 8919236090)
- **Manigala Mahitha** (ID: 99240041229 | Email: 99240041229@klu.ac.in | Phone: 8179761772)

