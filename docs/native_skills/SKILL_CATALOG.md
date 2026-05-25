# Native Skill Catalog

This catalog is generated from reviewed native skill manifests, command registry metadata, compatibility diagnostics, profile visibility, provenance/trust metadata, lockfile verification, tests, dogfood declarations, and docs paths.

The generated section is deterministic and should be refreshed with `python smart_agent.py skills docs-generate --write` after manifest or command-registry changes. It does not execute skills, external scripts, package managers, providers, connectors, or plugin runtimes.

<!-- BEGIN MANUAL NOTES -->
Add reviewed manual notes here. Do not edit the generated section by hand.
<!-- END MANUAL NOTES -->

<!-- BEGIN GENERATED NATIVE SKILL CATALOG -->

## Summary

- Skill count: 3
- Source: native skill manifests plus local metadata only
- Maturity behavior: copied from manifests; never inferred or upgraded by the generator
- Safety behavior: generated docs are advisory metadata and do not enable, install, or execute skills

## Skills

| Skill ID | Name | Description | Category | Status | Maturity | Risk | Trust | Profile visibility | Dependencies | Setup hints | Compatibility | Test status | Dogfood status | Provenance/trust | Lock status | Docs path | Commands | Known limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| native_skill_finder | Native Skill Finder | Search reviewed local native skill manifests, feature tracking docs, and candidate matrix records for requested capabilities. | productivity | available | 4 Tested | LOW | UNTRUSTED_DOCUMENT | personal_assistant, lead_response | capability:native_skills.find_skill, file:docs/FEATURE_REGISTRY.md, file:docs/FEATURE_MATURITY.md, platform:any | Uses local project metadata only; no external marketplace search or install. | status:supported | present:tests/test_native_skill_finder.py | not_declared | source:native, review:reviewed_local, trust:UNTRUSTED_DOCUMENT | missing | docs/native_skills/NATIVE_SKILLS_PROGRAM.md | python smart_agent.py skills find "<query>" | Matching is lightweight keyword/synonym scoring. |
| native_skill_vetter | Native Skill Vetter | Review candidate skill files and folders with static analysis before any native port or installation. | security | available | 4 Tested | LOW | UNTRUSTED_DOCUMENT | default, research, coding, personal_assistant, lead_response | capability:native_skills.inspect_skill, capability:native_skills.vet_skill_file, capability:native_skills.vet_skill_folder, capability:native_skills.score_candidate, capability:native_skills.report_last, platform:any | Built-in static inspector/vetter; no external skill execution, network access, plugin runtime, or dependency installation. | status:supported | present:tests/native_skills/test_skill_inspection_vetting.py | not_declared | source:native, review:reviewed_local, trust:UNTRUSTED_DOCUMENT | missing | docs/native_skills/SKILL_VETTING.md | python smart_agent.py skills vet <path_or_skill_id>, python smart_agent.py skills vet-folder <path>, python smart_agent.py skills score <path_or_skill_id>, python smart_agent.py skills show <skill_id>, python smart_agent.py skills validate [skill_id], python smart_agent.py skills doctor [skill_id], python smart_agent.py skills provenance <skill_id>, python smart_agent.py skills trust <skill_id>, python smart_agent.py skills inspect <path_or_skill_id>, python smart_agent.py skills report --last, python smart_agent.py skills compatibility <skill_id>, python smart_agent.py skills test <skill_id>, python smart_agent.py skills dogfood <skill_id> | Static heuristic vetting can miss obfuscated behavior., Static reports are review evidence only and do not authorize importing, enabling, or executing candidate skills. |
| pdf_workspace | PDF Workspace Skill | Read PDF metadata, extract embedded text, summarize, and perform best-effort table extraction for PDFs inside approved workspace roots. | documents | available | 4 Tested | MEDIUM | UNTRUSTED_DOCUMENT | default, research, coding, personal_assistant | capability:documents.pdf.read, capability:documents.pdf.extract_text, capability:documents.pdf.extract_tables, capability:documents.pdf.summarize, platform:any | Requires PDF files to be inside approved workspace roots; OCR and write actions are deferred. | status:supported | present:tests/test_pdf_documents.py | not_declared | source:native, review:reviewed_local, trust:UNTRUSTED_DOCUMENT | missing | docs/native_skills/pdf.md | python smart_agent.py pdf info <path>, python smart_agent.py pdf extract-text <path>, python smart_agent.py pdf summarize <path>, python smart_agent.py pdf extract-tables <path> | Embedded text only; OCR and PDF writes are disabled. |

## Missing Docs

No missing docs detected.

<!-- END GENERATED NATIVE SKILL CATALOG -->
