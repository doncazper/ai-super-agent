# arXiv Official API Provider

Status: framework/stub.

The arXiv official API provider declares arXiv public domains and normalizes mocked paper metadata to `SearchResult`-compatible records. It performs no live API calls by default.

Commands:

```bash
python smart_agent.py web api-status arxiv
python smart_agent.py web api-search arxiv "retrieval augmented generation"
```

`ARXIV_OFFICIAL_API_ENABLED=false` is the safe default until a live connector is explicitly implemented and tested. Returned paper metadata remains `UNTRUSTED_WEB`.
