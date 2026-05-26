<<<PROMPT_PACK_START>>>
pack_id: creative-media-generation-v1
pack_title: Creative Media Generation Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack builds the Creative Media Generation foundation for image, video, audio, music, TTS, thumbnails, social creatives, and future creative workflows.
  - It starts with provider registry, asset management, prompt/output safety, ComfyUI strategy/stub, and dogfood/evals before heavy model installs.
  - It should not install models, download models, call paid APIs, or generate unsafe content by default.
  - It should integrate with the existing ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, Command Registry, Feature Maturity, Prompt Tracker, and QA systems.
  - It should use free/local/open providers where possible, but track licenses and commercial restrictions.
  - Generated assets must be stored in a controlled media workspace and logged/audited.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not install models or dependencies unless explicitly approved.
  - Do not download large models automatically.
  - Do not call paid APIs by default.
  - Do not upload generated media anywhere.
  - Do not auto-publish to social platforms.
  - Do not generate or clone real people’s voices/faces without consent policy and approval.
  - Do not create impersonation workflows.
  - Do not claim commercial-use rights unless license evidence is tracked.
  - Do not store raw user prompts containing personal data in memory by default.
  - Do not create unsafe/NSFW/extremist/abusive media workflows.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Update docs/RELEASE_CHECKLIST.md where release-gate checks change.
  - Update docs/PROMPT_LEDGER.md / docs/PROMPT_QUEUE.md / docs/PROMPT_AUDIT.md if prompt tracking exists.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - package_install_required
  - model_download_required
  - paid_api_required
  - personal_data_access_required
  - real_person_likeness_or_voice_requested_without_policy
  - unsafe_media_request_required
  - commercial_license_unclear_for_required_model
  - background_persistence_required
  - security_policy_change_required
  - ambiguous_requirements

expected_prompt_ids:
  - MEDIA-01
  - MEDIA-02
  - MEDIA-03
  - MEDIA-04
  - MEDIA-05
  - MEDIA-06
  - MEDIA-07
  - MEDIA-08
  - MEDIA-09
  - MEDIA-10
  - MEDIA-11
  - MEDIA-12

<<<PROMPT_START id="MEDIA-01" order="1">>
title: Creative media roadmap and risk model
category: media
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Creative Media Generation roadmap and risk model.

Goal:
Define a safe, provider-based architecture for image, video, sound, music, TTS, thumbnails, social creatives, and future creative media workflows.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Follow the mini-SDLC.

Scope:
- Documentation and roadmap.
- No model/provider runtime implementation yet.
- No media generation yet.

Non-goals:
- Do not install ComfyUI or model dependencies.
- Do not download models.
- Do not call paid APIs.
- Do not generate media yet.
- Do not enable social publishing.
- Do not implement voice cloning.
- Do not implement real-person likeness workflows.

Create:
- docs/media/CREATIVE_MEDIA_GENERATION_TRACK.md
- docs/media/MEDIA_PROVIDER_STRATEGY.md
- docs/media/MEDIA_RISK_MODEL.md
- docs/media/MEDIA_LICENSE_POLICY.md
- docs/media/MEDIA_ASSET_POLICY.md
- docs/media/MEDIA_SAFETY_POLICY.md
- docs/decisions/creative_media_generation_architecture.md

Define provider categories:
- image_generation
- image_editing
- image_to_video
- text_to_video
- audio_generation
- music_generation
- tts
- voice_generation
- video_editing
- thumbnail/social_creative
- mock/test

Define candidate providers:
- ComfyUI
- Diffusers
- Stable Diffusion / SDXL
- FLUX
- Stable Diffusion 3.x
- Qwen-Image
- Wan / LTX / HunyuanVideo / Stable Video Diffusion
- AudioCraft / MusicGen / AudioGen
- Stable Audio Open
- ACE-Step
- TTS providers, future only
- Cloud providers, optional and disabled by default
- mock provider for tests

Define risk levels:
- media provider status: SAFE
- prompt planning: LOW
- local image generation: MEDIUM
- image editing with user images: MEDIUM/HIGH depending personal likeness
- video generation: MEDIUM/HIGH due cost/resources/content risk
- audio/music generation: MEDIUM
- voice cloning: CRITICAL or FORBIDDEN unless explicit consent workflow exists
- social posting/uploading: CRITICAL
- paid API generation: approval/config-gated
- real-person likeness generation: approval/policy-gated
- copyrighted/style imitation risk: review/caveat-gated
- unsafe/NSFW/extremist/abusive media: FORBIDDEN unless a future policy explicitly allows narrow safe cases

Planned commands to add to COMMAND_REGISTRY as planned/stubbed:
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media assets list
- python smart_agent.py media generate image "prompt"
- python smart_agent.py media generate video "prompt"
- python smart_agent.py media generate audio "prompt"
- python smart_agent.py media generate music "prompt"
- python smart_agent.py media thumbnail "prompt"
- python smart_agent.py media workflow list
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media license report
- python smart_agent.py media dogfood

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if present
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- CHANGELOG.md

Run docs validation/tests if available.

Final report:
- docs created
- planned commands
- risks added
- tests/validations run
- next recommended prompt
<<<PROMPT_END id="MEDIA-01">>

<<<PROMPT_START id="MEDIA-02" order="2">>
title: Media provider registry and output asset manager
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Media Provider Registry and Output Asset Manager.

Goal:
Create provider-neutral models and a controlled asset workspace for generated media.

Scope:
- Models.
- Provider registry.
- Asset manager.
- Tests.
- No real generation providers yet.

Non-goals:
- Do not generate media.
- Do not install providers.
- Do not call paid APIs.
- Do not upload/publish assets.
- Do not access personal photos/videos outside approved inputs.

Create:
- agent/media/
  - __init__.py
  - models.py
  - provider_registry.py
  - asset_manager.py
  - errors.py
  - redaction.py
- tests/media/test_media_models_registry.py
- tests/media/test_media_asset_manager.py
- docs/media/MEDIA_PROVIDER_REGISTRY.md
- docs/media/MEDIA_ASSET_MANAGER.md

Models:
- MediaProvider
- MediaProviderStatus
- MediaProviderCapability
- MediaGenerationRequest
- MediaGenerationResult
- MediaAsset
- MediaAssetType
- MediaPrompt
- MediaSafetyReview
- MediaLicenseInfo
- MediaProviderError

Asset fields:
- asset_id
- asset_type
- path
- created_at
- provider
- prompt_hash
- prompt_redacted
- source_inputs
- metadata
- license_info
- safety_status
- audit_ids
- retention_status

Asset manager requirements:
1. Store generated outputs under a controlled media workspace, e.g. media_outputs/ or workspace/media/.
2. Do not write outside approved roots.
3. Prompt text redacted where needed.
4. Personal input images/videos require explicit tagging and approval later.
5. Asset metadata JSON stored alongside output.
6. No raw secrets.
7. No auto-publish.
8. Deletion/cleanup bounded to media workspace.
9. Asset list/status commands read-only.
10. Tests use fake assets only.

Commands:
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media assets list
- python smart_agent.py media assets show <asset_id>
- python smart_agent.py media assets cleanup --dry-run

Tests:
- provider registry loads mock provider.
- unknown provider handled.
- asset path bounded.
- path traversal blocked.
- metadata written for fake asset.
- cleanup dry-run writes nothing.
- prompt redaction works.
- command registry updated.

Update docs/tracking.

Final report:
- provider registry added
- asset manager added
- commands added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-02">>

<<<PROMPT_START id="MEDIA-03" order="3">>
title: Media prompt/output safety, copyright, consent, and license policy
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build media prompt/output safety, copyright, consent, and license policy.

Goal:
Before generation providers are added, define and implement a safety preflight that classifies media prompts, identifies policy/consent/license risks, and blocks/flags unsafe requests.

Scope:
- Safety docs.
- Prompt safety checker.
- License metadata model.
- Tests.
- No generation.

Non-goals:
- Do not implement media generation.
- Do not call external moderation APIs.
- Do not build voice cloning.
- Do not create real-person impersonation workflows.
- Do not provide legal advice; provide operational risk flags.

Create:
- agent/media/safety.py
- agent/media/licenses.py
- tests/media/test_media_safety_license.py
- docs/media/MEDIA_PROMPT_SAFETY.md
- docs/media/MEDIA_COPYRIGHT_AND_LICENSE_POLICY.md
- docs/media/MEDIA_CONSENT_POLICY.md

Safety categories:
- safe_general
- commercial_use_unclear
- copyrighted_character_or_brand
- living_person_likeness
- private_person_likeness
- celebrity_likeness
- voice_clone
- impersonation
- sexual_content
- graphic_violence
- extremist_or_hate
- illegal_instructional_content
- medical/legal/financial claim risk
- political persuasion risk
- privacy_sensitive_input
- unknown_risk

Safety outcomes:
- allow
- warn
- require_license_review
- require_consent
- require_human_review
- deny

Requirements:
1. Prompt safety runs before generation.
2. License review required for provider/model commercial-use uncertainty.
3. Voice cloning requires explicit consent workflow; otherwise denied/deferred.
4. Real-person likeness requires consent/human review.
5. Unsafe categories denied.
6. Output metadata includes safety outcome.
7. Safety checker is deterministic first; model-based later optional.
8. No external calls.
9. Tests cover categories.
10. Command registry updated if command added.

Commands:
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media license report
- python smart_agent.py media consent policy

Tests:
- safe prompt allowed.
- celebrity/voice clone flagged.
- copyrighted character flagged.
- unsafe content denied.
- commercial uncertainty warns.
- consent required for real-person likeness.
- license info attached to mock provider.
- command registry updated.

Update docs/tracking.

Final report:
- safety checker added
- license policy added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-03">>

<<<PROMPT_START id="MEDIA-04" order="4">>
title: ComfyUI provider strategy and stub
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build ComfyUI provider strategy and stub.

Goal:
Prepare ComfyUI as the primary local workflow engine candidate for image/video/audio diffusion workflows without requiring installation or model downloads yet.

Scope:
- Provider stub.
- Config.
- Doctor/status.
- Mocked tests.
- Docs.

Non-goals:
- Do not install ComfyUI.
- Do not start ComfyUI server.
- Do not download models.
- Do not run workflows.
- Do not generate media yet.

Create:
- agent/media/providers/
  - __init__.py
  - comfyui.py
- tests/media/test_comfyui_provider_stub.py
- docs/media/providers/COMFYUI_PROVIDER.md
- docs/decisions/comfyui_provider_strategy.md

Config:
- COMFYUI_ENABLED=false
- COMFYUI_BASE_URL=http://127.0.0.1:8188
- COMFYUI_TIMEOUT_SECONDS=120
- COMFYUI_OUTPUT_DIR=
- COMFYUI_ALLOW_WORKFLOW_SUBMIT=false by default
- COMFYUI_ALLOW_CUSTOM_NODES=false by default unless reviewed
- COMFYUI_REQUIRE_SAFETY_PREFLIGHT=true

Provider status:
- disabled
- not_configured
- server_unreachable
- reachable
- workflow_submit_disabled
- ready_mock_only
- ready

Commands:
- python smart_agent.py media comfyui doctor
- python smart_agent.py media providers
- python smart_agent.py media workflows list --provider comfyui

Requirements:
1. Disabled by default.
2. No generation submissions by default.
3. Health check does not submit workflow.
4. Custom nodes treated as supply-chain risk.
5. Workflow JSON treated as UNTRUSTED_DOCUMENT unless vetted.
6. Provider errors normalized.
7. Mock tests only.
8. Command registry updated.

Tests:
- provider disabled by default.
- missing config setup hint.
- mock server reachable.
- workflow submit denied by default.
- custom nodes warning.
- provider registry lists comfyui.
- command registry updated.

Update docs/tracking.

Final report:
- ComfyUI stub added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-04">>

<<<PROMPT_START id="MEDIA-05" order="5">>
title: Image generation provider track
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build image generation provider track scaffolding.

Goal:
Prepare image generation workflows using free/local/open providers while keeping generation disabled/stubbed until providers/models are configured and safe.

Scope:
- Image request/result models if not already present.
- Mock image provider.
- Provider strategy docs.
- Tests.
- No actual image generation.

Non-goals:
- Do not download models.
- Do not install diffusion libraries.
- Do not call paid APIs.
- Do not generate real images.
- Do not use personal photos without explicit future consent flow.

Create:
- agent/media/providers/mock_image.py
- agent/media/image_generation.py
- tests/media/test_image_generation_scaffolding.py
- docs/media/IMAGE_GENERATION_STRATEGY.md
- docs/media/providers/IMAGE_PROVIDER_CANDIDATES.md

Candidate providers/models to document:
- ComfyUI workflows
- Diffusers local provider
- SDXL
- FLUX.1-schnell / FLUX.1-dev
- Stable Diffusion 3.x
- Qwen-Image
- ControlNet/LoRA workflows, future

Commands:
- python smart_agent.py media generate image "prompt" --dry-run
- python smart_agent.py media image providers
- python smart_agent.py media image plan "prompt"

Requirements:
1. Dry-run by default for unconfigured providers.
2. Safety preflight required.
3. License info required for provider/model before commercial-use claims.
4. Mock provider can create fake metadata/result for tests.
5. Real provider unavailable returns setup hint.
6. Output asset manager used for any generated/fake outputs.
7. No personal image editing yet.
8. Command registry updated.

Tests:
- dry-run plan generated.
- unsafe prompt blocked.
- license uncertainty warning.
- mock image result metadata created.
- unconfigured provider setup hint.
- asset manager integration.
- command registry updated.

Update docs/tracking.

Final report:
- image generation scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-05">>

<<<PROMPT_START id="MEDIA-06" order="6">>
title: Image editing, thumbnail, and social creative workflows
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build image editing, thumbnail, and social creative workflow scaffolding.

Goal:
Support future use cases such as YouTube thumbnails, real estate marketing graphics, vlog title cards, podcast covers, and social media images.

Scope:
- Workflow definitions.
- Dry-run planning.
- Mock outputs.
- Docs/tests.
- No real image editing yet.

Non-goals:
- Do not edit real user images by default.
- Do not generate real media.
- Do not upload/post.
- Do not create real-person likeness edits without future consent policy.

Create:
- agent/media/creative_workflows.py
- tests/media/test_creative_workflows.py
- docs/media/THUMBNAIL_SOCIAL_CREATIVE_WORKFLOWS.md

Workflow types:
- youtube_thumbnail
- short_form_video_cover
- podcast_cover
- real_estate_listing_graphic
- food_review_thumbnail
- family_vlog_title_card
- social_post_image
- ad_creative
- before_after_layout
- product_mockup

Commands:
- python smart_agent.py media thumbnail "prompt" --dry-run
- python smart_agent.py media creative plan "prompt"
- python smart_agent.py media creative templates

Requirements:
1. Workflow planning only by default.
2. Safety preflight runs.
3. Output size/aspect ratio suggestions.
4. Prompt templates stored as docs/config, not model secrets.
5. Asset manager integration.
6. No upload/publish.
7. Command registry updated.

Tests:
- thumbnail plan generated.
- social creative templates listed.
- unsafe prompt denied.
- commercial/license caution included where relevant.
- mock asset metadata created.
- command registry updated.

Update docs/tracking.

Final report:
- creative workflows scaffolded
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-06">>

<<<PROMPT_START id="MEDIA-07" order="7">>
title: Video generation provider strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build video generation provider strategy and scaffolding.

Goal:
Prepare for text-to-video and image-to-video generation using local/free providers where possible, while keeping actual generation disabled until providers/models are configured and tested.

Scope:
- Video provider strategy.
- Mock video provider.
- Request/result models if needed.
- Tests/docs.

Non-goals:
- Do not download video models.
- Do not install video generation dependencies.
- Do not generate real videos.
- Do not upload/post videos.
- Do not generate real-person likeness videos without future consent workflow.

Create:
- agent/media/providers/mock_video.py
- agent/media/video_generation.py
- tests/media/test_video_generation_scaffolding.py
- docs/media/VIDEO_GENERATION_STRATEGY.md
- docs/media/providers/VIDEO_PROVIDER_CANDIDATES.md

Candidate models/providers to document:
- ComfyUI video workflows
- Wan
- LTX-Video
- HunyuanVideo
- Stable Video Diffusion
- image-to-video workflows
- text-to-video workflows

Commands:
- python smart_agent.py media generate video "prompt" --dry-run
- python smart_agent.py media video providers
- python smart_agent.py media video plan "prompt"

Requirements:
1. Dry-run by default.
2. Safety preflight required.
3. Hardware/resource requirements documented.
4. Provider license tracked.
5. Mock video result for tests.
6. No real generation until configured.
7. No upload/publish.
8. Command registry updated.

Tests:
- dry-run plan generated.
- resource warning included.
- unsafe prompt denied.
- mock video metadata created.
- unconfigured provider setup hint.
- command registry updated.

Update docs/tracking.

Final report:
- video generation scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-07">>

<<<PROMPT_START id="MEDIA-08" order="8">>
title: Audio, music, and sound generation strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build audio, music, and sound generation strategy and scaffolding.

Goal:
Prepare for text-to-sound, text-to-music, short music beds, podcast intros, sound effects, and video backing tracks using local/free providers where possible.

Scope:
- Audio/music provider strategy.
- Mock audio provider.
- Request/result models if needed.
- Tests/docs.

Non-goals:
- Do not install audio/music models.
- Do not download models.
- Do not generate real audio.
- Do not clone voices.
- Do not generate copyrighted song/artist imitations as commercial output.
- Do not upload/publish.

Create:
- agent/media/providers/mock_audio.py
- agent/media/audio_generation.py
- tests/media/test_audio_generation_scaffolding.py
- docs/media/AUDIO_MUSIC_GENERATION_STRATEGY.md
- docs/media/providers/AUDIO_PROVIDER_CANDIDATES.md

Candidate providers/models:
- AudioCraft / MusicGen / AudioGen
- Stable Audio Open
- Stable Audio Open Small
- ACE-Step
- ComfyUI audio workflows
- TTS providers, future only

Commands:
- python smart_agent.py media generate audio "prompt" --dry-run
- python smart_agent.py media generate music "prompt" --dry-run
- python smart_agent.py media audio providers
- python smart_agent.py media music plan "prompt"

Requirements:
1. Dry-run by default.
2. Safety preflight required.
3. Voice cloning denied/deferred unless consent system exists.
4. Artist/track imitation flagged.
5. License/commercial-use warnings included.
6. Mock audio metadata for tests.
7. No real generation.
8. Command registry updated.

Tests:
- music plan generated.
- sound effect plan generated.
- voice clone request denied/deferred.
- artist imitation flagged.
- mock audio metadata created.
- command registry updated.

Update docs/tracking.

Final report:
- audio/music scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-08">>

<<<PROMPT_START id="MEDIA-09" order="9">>
title: TTS and voice generation strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-08"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build TTS and voice generation strategy.

Goal:
Prepare a safe path for future TTS and voice generation while explicitly separating ordinary TTS from voice cloning/impersonation.

Scope:
- Docs.
- Stub models/providers.
- Safety gates.
- Tests.

Non-goals:
- Do not implement voice cloning.
- Do not generate real voice audio.
- Do not imitate real people.
- Do not use personal voice samples.
- Do not upload/publish.

Create:
- agent/media/tts.py
- tests/media/test_tts_strategy.py
- docs/media/TTS_VOICE_GENERATION_STRATEGY.md
- docs/media/VOICE_CONSENT_POLICY.md

Voice categories:
- generic_tts
- character_voice
- user_owned_voice_with_consent
- public_figure_voice
- private_person_voice
- voice_clone
- impersonation

Rules:
1. Generic TTS can be future MEDIUM risk.
2. Voice cloning is CRITICAL or FORBIDDEN until consent system exists.
3. Public/private person voice imitation denied/deferred.
4. Consent records required before any future user-owned voice cloning.
5. Voice outputs require watermark/provenance strategy if implemented later.
6. No real generation in this prompt.

Commands as planned/stubbed:
- python smart_agent.py media tts plan "text"
- python smart_agent.py media voice consent-policy
- python smart_agent.py media voice providers

Tests:
- generic TTS plan allowed/stubbed.
- public figure voice denied.
- private person voice denied.
- user-owned voice requires consent.
- command registry updated.

Update docs/tracking.

Final report:
- TTS strategy added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-09">>

<<<PROMPT_START id="MEDIA-10" order="10">>
title: Media workflow commands and natural-language routing
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build media workflow commands and natural-language routing hooks.

Goal:
Make media generation discoverable and routable from natural-language requests without executing generation unsafely.

Scope:
- CLI command stubs/planners.
- NL routing hooks if natural-language system exists.
- Command registry.
- Tests.

Non-goals:
- Do not generate real media.
- Do not call providers.
- Do not upload/post.
- Do not execute unsafe prompts.

Commands:
- python smart_agent.py media plan "request"
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media assets list
- python smart_agent.py media generate image "prompt" --dry-run
- python smart_agent.py media generate video "prompt" --dry-run
- python smart_agent.py media generate audio "prompt" --dry-run
- python smart_agent.py media generate music "prompt" --dry-run
- python smart_agent.py media thumbnail "prompt" --dry-run

Natural-language examples:
- make me a thumbnail for this vlog
- create a 10-second intro animation
- make a lo-fi music bed for a food review
- generate sound effects for my video
- turn this image into a short video
- make a podcast cover
- create a real estate listing graphic

Requirements:
1. Dry-run/planning first.
2. Safety preflight before all generation planning.
3. Real generation blocked until provider configured.
4. NL routing creates plan/preflight, not automatic generation.
5. Command registry updated.
6. User guide/help updated if present.
7. Tests cover routing if system exists.

Tests:
- media plan command works.
- image/video/audio/music dry-run works.
- unsafe prompt denied.
- missing provider setup hint.
- NL route maps thumbnail request if NL system exists.
- command registry updated.

Update docs/tracking.

Final report:
- commands added
- NL routing hooks
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-10">>

<<<PROMPT_START id="MEDIA-11" order="11">>
title: Media dogfood and eval suite
category: tests
risk_level: LOW
approval_gate: false
depends_on: ["MEDIA-10"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Creative Media dogfood and eval suite.

Goal:
Create tests and dogfood commands to validate media planning, provider status, asset management, safety checks, license warnings, and dry-run workflows.

Create:
- dogfood_suites/media_core.yaml
- dogfood_suites/media_safety.yaml
- dogfood_suites/media_image_planning.yaml
- dogfood_suites/media_video_audio_planning.yaml
- eval_cases/media/
- docs/media/MEDIA_DOGFOOD_RUNBOOK.md

Dogfood:
- media providers
- media doctor
- media assets list
- media safety-check safe prompt
- media safety-check unsafe prompt
- image dry-run
- video dry-run
- audio dry-run
- music dry-run
- thumbnail dry-run
- missing provider setup hint
- license warning fixture

Eval checks:
- no real generation
- no paid APIs
- no model downloads
- unsafe prompts denied
- voice clone denied/deferred
- license uncertainty warned
- assets bounded to workspace
- command registry complete

Commands:
- python smart_agent.py dogfood run media_core --session
- python smart_agent.py dogfood run media_safety --session
- python smart_agent.py eval run --media
- python smart_agent.py eval report --media

Tests:
- dogfood YAML validates.
- eval fixtures load.
- media safety tests pass.
- no real media generated.
- command registry updated.

Update docs/tracking.

Final report:
- dogfood/eval suites added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="MEDIA-11">>

<<<PROMPT_START id="MEDIA-12" order="12">>
title: Creative media release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["MEDIA-11"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Creative Media Generation release gate and maturity review.

Goal:
Validate that creative media generation groundwork is safe, provider-based, documented, tested, and ready for future provider implementation without adding unsafe media generation.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. media unit tests
7. media dogfood/eval suite with fixtures
8. media safety checks
9. asset manager bounds tests

Verify:
- media roadmap exists
- provider registry exists
- asset manager bounds outputs
- safety checker exists
- license policy exists
- consent policy exists
- ComfyUI stub disabled by default
- image/video/audio/music/TTS generation are dry-run/stubbed unless configured
- no real model downloads
- no paid API calls by default
- no auto-upload/publishing
- voice cloning denied/deferred
- real-person likeness consent-gated
- command registry updated
- feature maturity conservative

Create/update:
- docs/media/CREATIVE_MEDIA_RELEASE_GATE.md
- docs/media/CREATIVE_MEDIA_MATURITY_REVIEW.md

Maturity assessment:
- Creative media roadmap
- Provider registry
- Asset manager
- Safety/license/consent policy
- ComfyUI provider stub
- Image generation scaffolding
- Thumbnail/social workflows
- Video generation scaffolding
- Audio/music scaffolding
- TTS/voice strategy
- NL routing/commands
- Dogfood/evals
- Release gate

Update:
- CHANGELOG.md
- README.md if needed
- docs/USER_GUIDE.md if present
- docs/HELP.md if present
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- dogfood/eval results
- maturity score
- remaining blockers
- whether creative media groundwork is safe to rely on
- next recommended feature track
<<<PROMPT_END id="MEDIA-12">>

<<<PROMPT_PACK_END>>>
