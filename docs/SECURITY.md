# Safety, privacy and limitations

Use synthetic or lawfully authorized exports only. No phone extraction, unlock, bypass, malware or covert collection is implemented.

All runtime processing is offline. Uploaded contents are stored unencrypted in `data/cases.sqlite3`. Protect the computer and its filesystem. Delete the database only after stopping the server if you want to erase this application's stored cases; backups and downloaded reports must be handled separately.

The local web server binds to 127.0.0.1, validates Host, uses a random per-start session token, rejects cross-origin writes, has no CORS access and supplies restrictive CSP. Evidence strings are escaped before HTML display. Token possession is not user identity; other users/processes on the same computer may access local endpoints. Do not expose the app to a network or run a public reverse proxy.

The UI human-review checkbox and name are workflow controls, not identity authentication. Reports are backend-gated until explicit approval. Review approval is logged in the hash chain. Import acknowledgements do not establish legality.

Computed hashes verify the import snapshot. They do not authenticate device origin, independently validate exported per-record hashes, or make a legal chain-of-custody claim. Audit hashes detect accidental or un-rehashed edits; a privileged operator can rewrite/recompute the database. No notarization or digital signatures are implemented.

English/Hindi indicator coverage is small and unvalidated. There will be false positives and false negatives. OTP, PIN and urgent words can appear in legitimate messages. UPI identifiers are extracted as strings, not validated bank ownership. The temporal correlation tool does not verify shared sender, account identity or causality. No confidence scores are invented.

Evidence content that resembles instructions is never executed. The agent has no shell tool, no outbound reporting tool and no LLM prompt surface. Unknown artifacts are retained but may not be analyzed beyond timeline/identifier extraction.

Before production use: authenticated users and roles, encrypted storage, signed acquisition manifests, secured deployments, audit retention, relevant privacy/legal review, independent detection evaluation, human-factors testing and deployment controls.
