# Audio Provider Candidates

Status: MEDIA-08 metadata-only.
Last updated: 2026-05-25.

These candidates are planning metadata. Their presence does not mean provider availability, model installation, license approval, or generation support.

| Provider | Status | Default enabled | Real generation | Notes |
|---|---|---:|---:|---|
| Mock audio provider | stubbed | false | false | Test-only fake metadata/results. |
| AudioCraft / MusicGen / AudioGen | planned | false | false | Requires model, license, and runtime review. |
| Stable Audio Open | planned | false | false | Requires model/license/runtime review. |
| Stable Audio Open Small | planned | false | false | Smaller model still needs license review. |
| ACE-Step | planned | false | false | Music generation has copyright/style-imitation risk. |
| ComfyUI audio workflows | stubbed | false | false | Workflow submission remains disabled. |
| TTS providers | future | false | false | TTS is future-only; voice cloning remains denied/deferred. |

## Default Policy

- No provider is enabled by default.
- No model is downloaded.
- No runtime is installed.
- No paid API is called.
- No audio or music is generated.
- No audio is uploaded or published.
- No voice cloning workflow exists.

## License Warnings

Future provider work must review:

- model license
- provider terms
- commercial output rights
- training-data caveats
- attribution requirements
- artist/style imitation restrictions

Mock provider records grant no production rights.
