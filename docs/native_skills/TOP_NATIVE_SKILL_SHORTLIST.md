# Top Native Skill Shortlist

Date: 2026-05-23

This shortlist ranks local-native skill candidates by value, safety, workspace-bounded feasibility, and fit with the existing agent architecture. It is not an implementation approval.

## Top 10 Candidates

| Rank | Candidate | Priority | Why First | First Implementation Boundary |
|---:|---|---|---|---|
| 1 | Skill-vetter native | now | Makes every later native skill safer; low runtime risk | Read candidate records and produce rubric findings only |
| 2 | Skill-finder native | now | Helps discover reviewed local records without touching external marketplaces by default | Search `docs/native_skills` and local registry docs first |
| 3 | PDF native | now | High-value, workspace-bounded, fixture-testable | Read approved workspace PDFs, extract text/tables, cite pages, no writes by default |
| 4 | DOCX/PPTX/XLSX native | soon | High user value for real work artifacts | Read approved workspace Office files, summarize/extract, write derived outputs only through file policy |
| 5 | TDD/test workflow native | now | Strong leverage for this repo and low personal-data risk | Read code/tests, propose tests, optionally patch through workspace file tools |
| 6 | Code-review workflow native | now | Frequent, safe, workspace-bounded, aligns with existing review behavior | Read diffs/files and produce findings; fixes require separate file-tool actions |
| 7 | Architecture-review workflow native | now | Useful for major project decisions and specs | Read approved docs/code and produce ADR-style review |
| 8 | Source-grounded research native | now | Reuses existing hardened web research path | Brokered search/fetch with citations and fetch-failure reporting |
| 9 | Workspace document summarizer native | now | Generalizes PDF/Office/plain-text summarization safely | Workspace-bounded read/summarize, untrusted-document wrapper, no memory by default |
| 10 | Knowledge capture native | now | Reuses existing capture workflow and memory gates | Workspace capture only; memory promotion explicit and audited |

## Recommended First Implementation

Start with `skill-vetter native`.

Reason:

- It reduces risk before adding more native skills.
- It is docs/data driven.
- It requires no external code execution.
- It can be tested with local fixture candidate records.
- It maps cleanly to existing workspace file reads and docs validation.
- It can reject unsafe candidates before they reach implementation.

Expected first behavior:

1. Read a local candidate record.
2. Validate required fields.
3. Score against selection and disqualification criteria.
4. Emit `accepted_for_spec`, `needs_more_research`, `defer`, or `reject`.
5. Explain ToolBroker mapping, approval gates, memory behavior, trust labels, and audit requirements.
6. Execute no external code and install nothing.

## Candidates To Defer

| Candidate | Defer Reason |
|---|---|
| Email send | CRITICAL send action; requires real provider decision, exact preflight, Action Center, no approval reuse |
| Message send | No safe automatic send path yet; platform automation and privacy risks are high |
| Browser automation | Risk of cookies, sessions, forms, passwords, private profile data, and unintended account actions |
| Cloud deployment | Can mutate paid infrastructure, secrets, DNS, credentials, and production resources |
| Self-evolution | Can weaken policy, create persistence, or grant capabilities if not tightly gated |
| Unrestricted app automation | Often requires Accessibility, UI scripting, broad filesystem access, and fragile UI state |

## Highest-Risk Categories

1. Messaging/internal communications: personal content, social harm, send risk, private databases.
2. Email drafting/sending: sensitive body content, attachments, irreversible send actions.
3. Calendar/scheduling writes: invitations, conflicts, private event details.
4. Browser automation: session/cookie/form risks and account mutation.
5. Cloud deployment: secrets, billing, infrastructure mutation.
6. Self-improvement/capability evolution: policy weakening and persistence risks.

## Lowest-Risk High-Value Candidates

1. Skill-vetter native.
2. Skill-finder native.
3. Code-review workflow native.
4. TDD/test workflow native.
5. Source-grounded research native.
6. Workspace document summarizer native.
7. Knowledge capture native.

## Next Recommended Prompt

`NATIVE-SKILL-VETTER`

Build the native skill vetter as a local, testable, docs/data-only workflow. It should read candidate records, apply the criteria and risk model, produce a structured review, and execute no external code.
