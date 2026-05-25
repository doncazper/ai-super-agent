# Runtime Service Registry

The service registry is a catalog of lazy runtime services. Listing services must never instantiate heavy services or adapters.

## Default Services

- `core`
- `safety`
- `connectors`
- `memory`
- `promptops`
- `dogfood`
- `command_registry`
- `feature_maturity`
- `app_bridge`
- `platform_bridge`
- `scheduler`
- `self_improvement`

## Rules

- Services are metadata until explicitly loaded by an approved runtime path.
- Disabled services cannot be loaded implicitly.
- App/platform bridge services are disabled by default.
- Personal-data services stay disabled until a connector-specific approval/config path exists.
- Service loaders must not bypass `ToolBroker`.

## CLI

```bash
python smart_agent.py runtime services
```

