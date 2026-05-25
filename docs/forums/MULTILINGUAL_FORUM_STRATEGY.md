# Multilingual Forum Strategy

Status: local language layer implemented; cross-language forum research still planned

## Goal

Support multilingual forum discovery, reading, translation, and summarization while preserving source references and avoiding overclaims about cultural consensus or broad representativeness.

## Principles

- Detect language before summarization where practical.
- Preserve source IDs and original-language snippets.
- Use local model translation by default.
- Do not use paid or external translation APIs by default.
- Label translations as model-generated.
- Treat translated source text as untrusted source data.
- Do not store translations or summaries in memory by default.
- Preserve slang, platform-specific terms, and uncertain translations as notes.

## Translation Boundary

Translation is an interpretation layer, not a new source. A translated passage must keep a reference to the original source, original language, retrieved timestamp, and source type. If translation quality is uncertain, the answer must say so.

## Summarization Boundary

Forum summaries must distinguish:

- directly supported source claims,
- repeated anecdotal viewpoints,
- disagreement or conflicting source claims,
- model inference,
- language/translation uncertainty,
- sparse data limitations,
- and unavailable or blocked sources.

## Chinese And Asia-Language Support

Initial language coverage should include English, Chinese, Japanese, Korean, and Spanish fixtures, with simplified/traditional Chinese detection where practical. Cross-language research must avoid claiming regional or cultural consensus from sparse forum samples.

## Implemented Local Language Layer

The local v1 language layer now provides brokered `language.detect`, `language.translate_text`, `language.summarize_multilingual`, and `language.extract_terms` capabilities plus CLI commands:

```bash
python smart_agent.py language detect --text "..."
python smart_agent.py language translate --from auto --to en --text "..."
python smart_agent.py language translate-file ./workspace/input.txt --to en
python smart_agent.py language glossary ./workspace/input.txt
```

The implementation is deliberately local-first and conservative:

- detection is heuristic and local,
- translation uses LM Studio/Qwopus by default,
- unavailable local model config returns `setup_required`,
- no external or paid translation API is used by default,
- file translation/glossary commands read only approved workspace files through `filesystem.read`,
- translations are labeled `MODEL_GENERATED_TRANSLATION`,
- source IDs and chunk IDs are preserved,
- source text remains `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`,
- and no translations, summaries, glossary terms, or source content are written to memory by default.

Cross-language Reddit/forum research, source selection, and culturally cautious comparison remain planned follow-up work.
