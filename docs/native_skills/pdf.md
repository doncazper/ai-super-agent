# PDF Workspace Native Skill

PDF Workspace v1 is a reviewed local native skill for approved workspace PDFs.

## Commands

```bash
python smart_agent.py pdf info ./workspace/file.pdf
python smart_agent.py pdf extract-text ./workspace/file.pdf
python smart_agent.py pdf summarize ./workspace/file.pdf
python smart_agent.py pdf extract-tables ./workspace/file.pdf
```

## Capabilities

- `documents.pdf.read`
- `documents.pdf.extract_text`
- `documents.pdf.extract_tables`
- `documents.pdf.summarize`

## Safety Rules

- PDF paths are resolved through the same approved-root guard used by workspace files.
- Path traversal is blocked.
- Private macOS folders and denied filenames remain blocked.
- PDF content is labeled `UNTRUSTED_DOCUMENT`.
- OCR is disabled by default.
- Embedded PDF scripts, actions, attachments, and forms are not executed.
- No external binaries are executed.
- File size, page, and extracted-text limits are enforced.
- Document content is not stored in memory by default.
- All operations execute through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

## Current Behavior

`pdf info` reads page count, file size, encryption state, and safe metadata.

`pdf extract-text` extracts embedded PDF text with `pypdf`. It does not OCR scanned pages.

`pdf summarize` creates a deterministic local preview and keyword list. It filters obvious instruction-injection text and is not an LLM synthesis.

`pdf extract-tables` uses a conservative text-line heuristic. If a clear delimited table is not detected, it returns an empty `tables` list rather than inventing rows.

## Deferred

- OCR support.
- PDF split/merge.
- Writing derived PDFs.
- Dedicated table extraction dependency.

These require separate review because they can add new dependencies, output files, or approval behavior.
