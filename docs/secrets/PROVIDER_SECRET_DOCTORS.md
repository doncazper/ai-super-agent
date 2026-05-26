# Provider Secret Doctors

Provider secret doctors report configuration presence and setup guidance without using secret values.

Supported provider selectors:

- `reddit`
- `serpapi`
- `brave`
- `weatherapi`
- `telegram`
- `gmail`
- `newsapi`
- `mediacloud`
- `microsoft`
- `github`
- `media`
- `lmstudio`
- `ollama`
- `llama_cpp`
- `all`

Example:

```bash
python smart_agent.py secrets doctor reddit
python smart_agent.py secrets doctor all
```

Rules:

- Output is present/missing metadata only.
- OAuth/client secrets, API keys, tokens, and token paths are redacted.
- Paid/quota providers remain disabled unless explicit cost policy allows them.
- Gmail and Microsoft broad scopes are warning metadata, not permission grants.
- Media providers remain disabled/stubbed; ComfyUI base URL is config, not a secret.
- LM Studio/Ollama/llama.cpp entries are local runtime config checks, not secret checks.
- Doctors do not call provider APIs, read inbox/chats/files, send messages, generate media, or enable providers.
