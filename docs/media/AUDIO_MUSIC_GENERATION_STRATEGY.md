# Audio, Music, And Sound Generation Strategy

Status: MEDIA-08 local scaffold.
Last updated: 2026-05-25.

## Scope

MEDIA-08 prepares a safe boundary for future text-to-sound, text-to-music, podcast intro, sound effect, and backing-track workflows.

Current support is limited to:

- audio/music provider candidate metadata
- dry-run audio and music plans
- deterministic safety preflight
- voice-cloning denial metadata
- artist/track imitation warnings
- license/commercial-use warnings
- fake audio/music metadata helpers for tests

## Non-Goals

MEDIA-08 does not:

- Install audio/music models.
- Download models.
- Import audio/music generation SDKs.
- Generate real audio or music.
- Clone voices.
- Generate copyrighted song or artist imitations as commercial output.
- Upload or publish audio.
- Add TTS runtime behavior.
- Call paid APIs.

## Commands

```bash
python smart_agent.py media generate audio "prompt" --dry-run
python smart_agent.py media generate music "prompt" --dry-run
python smart_agent.py media audio providers
python smart_agent.py media music plan "prompt"
```

`media generate audio` and `media generate music` require `--dry-run`. Non-dry-run execution is blocked.

All commands route through ToolBroker and PolicyEngine.

## Voice And Imitation Policy

Voice cloning is denied/deferred until a future explicit consent workflow exists.

Artist, track, and recognizable style imitation requests are flagged for license review. The scaffold does not allow commercial output that imitates copyrighted songs, recognizable recordings, or living artists.

## License Policy

Music and sound generation has heightened copyright and commercial-use risk. Plans include:

- provider/model license uncertainty
- artist imitation flags
- commercial-use review requirement
- no legal advice disclaimer

Mock provider records grant no production usage rights.

## Mock Provider

`agent.media.providers.mock_audio.MockAudioProvider` exists for tests and mock metadata only.

It can create fake `.txt` fixture assets under the controlled media workspace through `MediaAssetManager`. These are not audio files and grant no usage rights.

## Future Gate

Before any real audio or music provider can run, the repo must add:

- exact capability manifest entries
- ToolBroker mapping
- PolicyEngine tests
- ApprovalManager behavior for HIGH/CRITICAL cases
- AuditLogger fields for provider decisions, prompt safety, license warnings, denials, approvals, asset writes, and results
- model/provider license review
- startup overhead/import tests
- mock and live opt-in validation
