# Creative Media Dogfood And Eval Runbook

Status: MEDIA-11 mock/fixture-first dogfood and eval coverage.
Last updated: 2026-05-25.

## Safety Boundary

Creative media dogfood is local and planning-only. It must not generate, edit, upload, publish, or download media. It must not call paid APIs, install models, start provider runtimes, read personal images/videos/audio/voice samples, or infer consent.

All suite commands use existing status, preflight, dry-run, setup-hint, or fixture-backed eval paths.

## Dogfood Suites

Run these only inside an explicit dogfood session:

```bash
python smart_agent.py session start --name media-dogfood
python smart_agent.py dogfood run media_core --session
python smart_agent.py dogfood run media_safety --session
python smart_agent.py dogfood run media_image_planning --session
python smart_agent.py dogfood run media_video_audio_planning --session
```

The suites live at:

- `dogfood_suites/media_core.yaml`
- `dogfood_suites/media_safety.yaml`
- `dogfood_suites/media_image_planning.yaml`
- `dogfood_suites/media_video_audio_planning.yaml`

## Eval Commands

```bash
python smart_agent.py eval run --media
python smart_agent.py eval report --media
```

The fixture cases live under `eval_cases/media/` and check:

- no real generation
- no paid APIs
- no model downloads
- unsafe prompts denied before planning
- voice clone and person-voice imitation denied/deferred
- license uncertainty warnings present
- assets bounded to `workspace/media`
- command registry coverage for media dogfood/eval commands

## Failure Signals

Stop and open a bug if any media dogfood/eval output shows:

- `generated_media=true`
- a provider/network call for generation
- model download or package install requirement
- paid API use by default
- upload or publish enabled
- voice cloning enabled
- unsafe prompt allowed
- personal media/source audio/source video/voice sample read
- raw prompt, secret, or personal data in session logs

## Release-Gate Notes

MEDIA-11 proves only local mock/fixture coverage. It is not live validation and does not make creative media user-ready for real generation. MEDIA-12 must keep maturity conservative and verify that all real provider actions remain unavailable, disabled, or future-gated.
