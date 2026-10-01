# Architecture and agent flow

```text
Authorized exported evidence + objective
          |
     Intake role — validate, normalize, hash, persist
          |
     Planner role — route objective; choose allowed tools
          |
     Integrity tool → Timeline tool → optional Entity tool → optional Scan tool
          |
     Planner inspects scan output + available payment types
          |                         |
       conditions met          conditions absent
          |                         |
     add Correlation tool       skip; record reason
          \                         /
           Citation validator + Reporting role
                         |
              Persist review packet + audit
                         |
          Human review / explicit approval + note
                         |
               Append approval audit event
                         |
           Export reviewed Markdown report + audit JSON
```

## Role contracts
- Intake: records and import warnings, no authenticity claim.
- Planner: explicit keyword intent routing and tool selection.
- Triage: message indicator scan, identity extraction, UTC timeline.
- Correlation: flag payments 0–1,800 seconds after flagged communications.
- Reporting: validate evidence IDs, save packet, gate final report.
- Human: inspect raw cited records and approve as self-declared reviewer.

## Decision policy
`timeline`, `chronology`, or `समय` selects timeline only (plus integrity).
`contact`, `entities`, `identifier`, or `संपर्क` selects identifiers and timeline.
Everything else selects fraud triage. The UI exposes all supported routes.

Only code-defined tools execute. Evidence and goals are data, not executable prompts. No external network tools or shell-execution tools are exposed to the agent.

## Persistence
`cases`: case ID and JSON record including immutable-by-application records, warnings, import acknowledgement and import digests.
`runs`: run ID, case ID and JSON packet including findings, plan trace, audit hashes and review state.
Database access is serialized with a thread lock. A new run is needed to amend an approved review.

## API
GET `/api/session` initializes a local browser token.
Other `/api/*` endpoints require `X-Session-Token`.
- GET `/api/cases`, `/api/cases/{id}`, `/api/demo`
- POST `/api/import`: title, raw, filename, mode, authorized
- POST `/api/run`: case_id, goal
- POST `/api/approve`: run_id, reviewer, note, confirmed
- GET `/api/report/{run_id}`: HTTP 409 until approved
- GET `/api/audit/{run_id}`: review packet and audit JSON

## Scalability and feasibility
Current limits: 5 MB, 5,000 records, one local server. Correlation is an O(messages × payments) scan, not designed for massive collections. A production version would use indexed event windows, jobs, authenticated reviewer accounts, encrypted evidence storage, signed acquisition manifests and independently evaluated detectors. These are roadmap items, not implemented capabilities.
