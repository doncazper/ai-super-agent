# Native Skill Candidates

This file is the working candidate registry for skills that may become native capabilities.

Status values:

- candidate
- researched
- specified
- scaffolded
- implemented
- tested
- hardened
- live-validated
- native-pattern
- rejected
- deferred

| Candidate ID | Name | Category | Status | Source | User Value | Likely ToolBroker Mapping | Risk | Trust | License Status | Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NS-PROGRAM-FOUNDATION | Native Skills Program foundation | self-improvement | specified | local project requirement | Gives the project a safe intake path before considering third-party skill ideas | Docs and validation only; no runtime tool | LOW | TRUSTED_USER / UNTRUSTED_DOCUMENT for future external skill text | n/a | accepted | This task creates the governance foundation only. |
| NS-SKILL-MARKETPLACE-SURVEY | Skill marketplace survey | research | candidate | future review | Identify useful public skill patterns without installing them | `web.search`, `web.fetch_url`, workspace docs | LOW/MEDIUM | UNTRUSTED_WEB | to be reviewed | queued | Next recommended prompt; research-only. |
| NS-NATIVE-SKILL-VETTER | Native skill vetter | security | candidate | future local design | Apply repeatable review checks to candidate records | workspace docs, policy docs, no execution | LOW | UNTRUSTED_DOCUMENT | n/a | queued | Should remain docs/test-first. |
| NS-NATIVE-SKILL-MANIFEST | Native skill manifest and loader | developer tools | candidate | future local design | Define local metadata for reviewed skills | config validation, docs, no unreviewed execution | MEDIUM | TRUSTED_USER / MODEL_OUTPUT | n/a | queued | Must not auto-enable unvetted skills. |
| NS-SKILL-FINDER | Skill finder native skill | research | tested | local implementation | Find existing reviewed local skills and candidate records | `native_skills.find_skill`; local docs/index only | LOW | UNTRUSTED_DOCUMENT metadata | n/a | accepted | Implemented as local-only search over manifests, native candidate docs, feature registry, and maturity tracker; no external marketplace browse/install/execute. |
| NS-PDF-WORKSPACE | PDF workspace native skill | documents | tested | local implementation | Read/summarize workspace PDFs safely | `documents.pdf.read`, `documents.pdf.extract_text`, `documents.pdf.extract_tables`, `documents.pdf.summarize` | MEDIUM | UNTRUSTED_DOCUMENT | pypdf project dependency | accepted | Workspace-bounded only; OCR, split/merge, generated PDF writes, and external binaries deferred. |
| NS-OFFICE-DOCS | DOCX/PPTX/XLSX native skill | documents | candidate | marketplace survey | Read and summarize approved workspace Office files | workspace file assistant, future document/spreadsheet helpers | MEDIUM | UNTRUSTED_DOCUMENT | to be reviewed per library | shortlisted | No macros, no private folders, writes only through file policy. |
| NS-TDD-WORKFLOW | TDD/test workflow native skill | testing | candidate | marketplace survey | Generate and run focused tests for approved project files | workspace files, test runner, git diff | LOW/MEDIUM | UNTRUSTED_DOCUMENT / MODEL_OUTPUT | n/a | shortlisted | High-value and workspace-bounded; patches must use file policy. |
| NS-CODE-REVIEW | Code-review workflow native skill | coding | candidate | marketplace survey | Review diffs and files for defects and missing tests | workspace files, git diff, test runner | LOW | UNTRUSTED_DOCUMENT / MODEL_OUTPUT | n/a | shortlisted | Read-only first; fixes require separate approved edits. |
| NS-ARCH-REVIEW | Architecture-review workflow native skill | coding | candidate | marketplace survey | Review architecture docs/code and propose ADR-style findings | workspace files, git diff, optional public web docs | LOW/MEDIUM | UNTRUSTED_DOCUMENT / MODEL_OUTPUT | n/a | shortlisted | No cloud or infrastructure mutations. |
| NS-RESEARCH | Source-grounded research native skill | research | candidate | marketplace survey | Reuse hardened web research as a discoverable native workflow | web search/fetch through ToolBroker | LOW/MEDIUM | UNTRUSTED_WEB | n/a | shortlisted | No fabricated sources; no search history memory by default. |
| NS-DOC-SUMMARIZER | Workspace document summarizer native skill | documents | candidate | marketplace survey | Summarize approved workspace documents with source context | filesystem read, future document extraction | LOW/MEDIUM | UNTRUSTED_DOCUMENT | n/a | shortlisted | No memory write by default. |
| NS-KNOWLEDGE-CAPTURE | Knowledge capture native skill | memory/notes | candidate | marketplace survey | Reuse workspace capture workflow as a native skill | capture workflow, memory policy | LOW/MEDIUM | TRUSTED_USER / UNTRUSTED_WEB / UNTRUSTED_DOCUMENT | n/a | shortlisted | Memory promotion remains explicit and audited. |

## Candidate Notes

- Candidate status is not implementation approval.
- Candidates must not be imported, installed, or executed.
- External skill source text must be reviewed as untrusted data.
- A candidate may stay in `candidate` status until a decision record exists.
