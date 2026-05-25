# Startup Overhead Policy

Runtime orchestration must not slow normal CLI startup with heavy imports or live checks.

## Lightweight Imports

Importing `agent.runtime` should not import:

- LM Studio clients;
- ToolBroker;
- connector adapters;
- native app bridge modules;
- browser automation;
- web providers;
- personal-data adapters.

## Runtime Doctor

`python smart_agent.py runtime doctor` may inspect runtime metadata and local safety boundaries. It must not call LM Studio, fetch network resources, read personal data, or start a scheduler.

## Regression Checks

The release gate should check:

- runtime import is lightweight;
- runtime status/doctor work without `LMSTUDIO_MODEL`;
- no background process is created;
- no personal-data connector is accessed;
- no runtime command executes tools directly.

