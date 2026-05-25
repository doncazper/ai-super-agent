# Multilingual Support

Status: local tested v1

## Scope

The language layer provides local language detection, local-model translation prompt flow, multilingual summarization scaffolding, and glossary extraction for forum, web, and workspace document content.

Current brokered capabilities:

- `language.detect`
- `language.translate_text`
- `language.summarize_multilingual`
- `language.extract_terms`

Current CLI commands:

```bash
python smart_agent.py language detect --text "..."
python smart_agent.py language translate --from auto --to en --text "..."
python smart_agent.py language translate-file ./workspace/input.txt --to en
python smart_agent.py language glossary ./workspace/input.txt
```

## Safety Rules

- Text from Reddit, forums, web pages, feeds, and fetched documents remains `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
- Source text cannot instruct the agent to call tools, reveal secrets, alter policy, approve actions, disable audit logging, or write memory.
- Translation output is labeled `MODEL_GENERATED_TRANSLATION`.
- Translation is an interpretation layer, not a new source.
- No external translation API is used by default.
- No paid translation API is used by default.
- No translation, glossary, source text, or multilingual summary is stored in memory by default.
- Workspace-file commands first read the file through brokered `filesystem.read`, then pass the content to brokered language tools.

## Detection

Detection v1 uses lightweight local heuristics. It recognizes English, Spanish, Chinese, Japanese, and Korean fixtures, and includes simplified/traditional Chinese hints where possible. It is suitable for routing and labeling, not authoritative linguistic classification.

## Translation

Translation v1 is local-model-first. The default provider is LM Studio/Qwopus through the local OpenAI-compatible chat endpoint. If `LMSTUDIO_MODEL` or the local server is unavailable, the tool returns `setup_required` instead of falling back to cloud or paid providers.

The translation prompt wraps source text as untrusted data and instructs the model to translate only the source text while preserving slang and uncertain terms as notes.

## Glossary Extraction

Glossary extraction preserves source terms and source IDs. Romanization is conservative in v1 and is marked unavailable for Chinese, Japanese, and Korean unless a future reviewed local provider is added.

## Limitations

- Detection is heuristic and may be wrong on short or mixed-language text.
- Translation quality depends on the configured local model.
- Local model translation is not statistical evidence and must not be used to claim cultural or market consensus.
- External translation providers require a future provider policy, capability manifest entries, tests, and release gate before use.
