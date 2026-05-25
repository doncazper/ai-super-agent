# Build Provenance

This file explains how to prove whether a feature exists, is merely planned, or was reconstructed from evidence.

## Evidence Types

Strong evidence:

- source code
- tests
- capability manifest entries
- command registry entries
- command test matrix rows
- completion report entries
- release checklist evidence
- feature registry and maturity rows
- prompt ledger state
- git commits

Weak evidence:

- roadmap entries
- future prompt text
- reconstructed prompt summaries
- notes without tests or code

## Source-Of-Truth Hierarchy

1. Code and tests.
2. Capability manifest and policy validation.
3. Command registry and command test matrix.
4. Completion report and release checklist.
5. Feature registry and maturity tracker.
6. Prompt ledger, queue, and audit.
7. Changelog.
8. Roadmap.
9. Reconstructed prompts and planning notes.

## Implemented Versus Planned

Implemented means code or docs exist at the expected paths and tests or validations cover the claim. Planned means the roadmap or prompt queue describes desired work but implementation evidence is absent.

## Stubbed Versus Complete

Stubbed features intentionally return setup notes, disabled status, or unsupported messages. Complete features still require conservative maturity and may need live validation before user-ready status.

## Original Versus Reconstructed Packs

Original prompt packs are stored under `prompts/packs/` and can be used as exact evidence. Reconstructed prompt packs are stored under `prompts/packs/reconstructed/`, labeled `status: reconstructed`, and include confidence and caveats.

## Avoid Overclaiming

Do not claim a prompt, feature, provider, connector, or bridge is exact, implemented, mature, live-validated, or user-ready unless the evidence hierarchy supports it.
