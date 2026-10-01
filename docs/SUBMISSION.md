# BHARAT AGENTIC 2026 — submission template

**Project name:** Bharat Evidence Agent
**Team members:**
- **Tumma Sevireddy** | ID: 99240040699 | Email: 99240040699@klu.ac.in | Phone: 7671975351
- **Pallapotu Balaji** | ID: 99240041234 | Email: 99240041234@klu.ac.in | Phone: 9392774307
- **Daggupati Vinusha** | ID: 99240041217 | Email: 99240041217@klu.ac.in | Phone: 8919236090
- **Manigala Mahitha** | ID: 99240041229 | Email: 99240041229@klu.ac.in | Phone: 8179761772
**Selected domain:** Citizen & GovTech

## Problem statement
Authorized mobile-evidence exports can contain messages, call logs and payments across languages. Manually triaging them makes it difficult to organize timelines, link review leads to their sources, and record which tools and reasoning steps were used.

## Solution overview
A local, offline deterministic agent ingests exports, plans relevant analysis, uses evidence tools, conditionally correlates payments, and prepares a human-review packet. Final report export is approval-gated. It supports a fictional Bharat-focused UPI scenario and English/Hindi communication indicators without relying on cloud processing.

## Agent workflow / architecture
Understand: validate case, objective and authorization acknowledgement.
Reason: determine supported objective and inspect available records/tool results.
Plan: choose whitelisted tools; conditionally extend plan after finding message leads.
Use tools: integrity, timeline, entities, communication scan, payment correlation.
Act: persist review packet, log human approval, export reviewed report.

## Technology stack
Python 3.10+ standard library, local HTTP server, SQLite, HTML/CSS/JavaScript, SHA-256. PPTX/PDF/video tools were used to prepare submission materials only and are not runtime dependencies. No LLM is used in the working agent.

**GitHub repository:** https://github.com/BALAJI0678/bharat-hackathon
**Working demo:** Run locally (`python server.py` -> `http://127.0.0.1:8787`) or via GitHub Actions (Actions -> Run Bharat Evidence Agent)
**Demo video:** docs/demo_video.mp4 (synthetic data, narrated walkthrough)
**Pitch deck:** docs/pitch_deck.pptx / docs/pitch_deck.pdf (5 slides)

## Judging alignment
- Agentic capability: tool selection, observable conditional replanning, tool execution, persistent local actions and human gate.
- Bharat impact: target workflow for authorized local triage; English/Hindi examples and UPI export scenario. Impact is a hypothesis; no adoption or savings are claimed.
- Technical implementation: 20 automated tests plus browser smoke test, durable storage, cited records and audit.
- Innovation: inspectable local plan and explicit integrity/causality limits, rather than generic chat.
- UX: one-click synthetic demo, source records, tabbed analysis and review gate.
- Scalability/feasibility: zero third-party runtime dependencies; modest local limits; documented production roadmap.
- Demo: actual app walkthrough and alternate-goal route.

## Before submission — required owner actions
- [ ] Obtain/read the official Guidelines PDF and check complete rules.
- [ ] Confirm eligibility and pre-existing code/reuse/AI-assistance rules.
- [ ] Disclose the supplied mobile-forensics source and the generated implementation as required.
- [ ] Fill in actual team members and contact details.
- [ ] Verify licensing; original_reference source rights were not established.
- [ ] Publish source to GitHub and replace the URL placeholder.
- [ ] Supply required working-demo access; a local app is not a hosted URL.
- [ ] Watch the video and check the organizers' format/file-size restrictions.
- [ ] Review the pitch deck and add actual team names if required.
- [ ] Confirm exact event date, timezone and submission channel. Pasted schedule: 8 PM opens / 9 PM deadline, no date/timezone provided.
- [ ] Upload all required items and verify acknowledgement before the deadline.

## Compliance statement
Official PDF unavailable. Only the pasted requirements were reviewed. Full official compliance, eligibility and the calendar deadline cannot be verified from them.
