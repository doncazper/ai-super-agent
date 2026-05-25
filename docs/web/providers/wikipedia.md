# Wikipedia Official API Provider

Status: framework/stub.

The Wikipedia official API provider declares Wikipedia, Wikidata, and MediaWiki public domains and normalizes mocked public page results to `SearchResult`-compatible records. It performs no live API calls by default.

Commands:

```bash
python smart_agent.py web api-status wikipedia
python smart_agent.py web api-search wikipedia "open source"
```

`WIKIPEDIA_OFFICIAL_API_ENABLED=false` is the safe default until a live connector is explicitly implemented and tested. Web content remains `UNTRUSTED_WEB`.
