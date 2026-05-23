<<<PROMPT_PACK_START>>>
pack_id: example-pack-v1
pack_title: Example Prompt Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="EXAMPLE-01" order="1">>
title: Example first prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
Paste the first prompt here.
<<<PROMPT_END id="EXAMPLE-01">>

<<<PROMPT_START id="EXAMPLE-02" order="2">>
title: Example second prompt
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["EXAMPLE-01"]
status: queued

PROMPT:
Paste the second prompt here.
<<<PROMPT_END id="EXAMPLE-02">>

<<<PROMPT_PACK_END>>>
