# Performance Overhead Policy for Platform Code

Cross-platform support must not make the existing Python agent slower, heavier, or more fragile.

## Startup Requirements

At core startup:

- Do not import platform-specific native frameworks.
- Do not import heavy bridge implementations.
- Do not call network APIs.
- Do not start subprocesses.
- Do not scan personal files.
- Do not request OS permissions.
- Do not start app bridge servers.
- Do not start polling loops or background workers.

CLI-only mode must remain fully functional even when no platform bridge is installed, configured, or supported.

## Acceptable Overhead Target

Platform groundwork should be measurable by import graph and behavior guard tests before precise timing tests. Timing assertions may be flaky across machines, so the primary gate is:

- Core import does not import bridge implementation modules.
- Bridge registries are lazy.
- Status/doctor commands read static metadata and safe config only.
- No network, subprocess, native framework, personal file scan, or server startup happens during import.

When timing is measured, platform planning/scaffold code should add negligible overhead compared with the existing CLI startup path. Any meaningful regression must be documented and fixed before release promotion.

## Lazy Loading Rule

The bridge registry may know that a bridge exists, but it must not import or initialize the bridge implementation until a brokered command needs metadata or execution. For metadata commands, prefer static capability records over importing adapters.

## Detection, Config, And Paths

Platform detection and config scaffolding must stay metadata-only:

- Detection uses `sys.platform` and explicit environment flags only.
- Detection failures return `platform=unknown` and setup guidance instead of crashing.
- Detection may use a small cache, default `PLATFORM_DETECTION_CACHE_SECONDS=300`.
- Platform bridge flags default to disabled: `PLATFORM_BRIDGES_ENABLED=false`, `MACOS_BRIDGE_ENABLED=false`, `IOS_COMPANION_BRIDGE_ENABLED=false`, `WINDOWS_BRIDGE_ENABLED=false`, and `WEB_APP_BRIDGE_ENABLED=false`.
- App bridge flags default to inert local contract mode: `APP_BRIDGE_ENABLED=false`, `APP_BRIDGE_HOST=127.0.0.1`, `APP_BRIDGE_TRANSPORT=stdio`, `APP_BRIDGE_REQUIRE_PAIRING=true`, and `APP_BRIDGE_ALLOW_REMOTE=false`.
- `PLATFORM_LAZY_LOAD_BRIDGES=true` is the default and must remain the expected path.
- Path helpers compute project-local config/data/cache/log/workspace/report/state locations only; they do not call `Path.home()`, create directories, scan files, or apply new broad OS-specific filesystem assumptions.
- Existing filesystem denied/sensitive path policies remain authoritative. Windows denied/sensitive path rules are planned/stubbed metadata until a future reviewed implementation.

## Diagnostics

Future `platform doctor` and `platform status` commands should report:

- Detected platform.
- Runtime mode.
- Bridge mode.
- Lazy-load status.
- Disabled bridge flags.
- Unsupported or setup-required reasons.
- Warnings when bridge code would be imported too early.

Diagnostics must avoid personal-data reads and provider calls.

## Release Gate

Every future platform milestone must include checks for:

- No native framework import at core startup.
- No bridge action outside ToolBroker.
- No app bridge server by default.
- No personal file scan during detection/status.
- No network or subprocess calls during startup.
- Structured unsupported behavior on non-target platforms.
