# Aigent RE Project Index

This repository is the planning and early architecture home for **Aigent RE**, an AI-native real estate intelligence platform for iOS, macOS, and later Android.

## Product Direction

Aigent RE is intended to become:

```text
PropertyRadar + PropStream + deeper public-record lead intelligence + AI CRM workflows
```

The product should not compete as a cheaper commodity data tool. It should compete by combining:

- Licensed property, owner, equity, deed, mortgage, and listing data.
- Direct public-record ingestion for fresher local lead signals.
- Search across NODs, BKs, probate, divorce/dissolution, tax delinquency, code violations, evictions, liens, judgments, permits, FSBO/listing events, and entity/LLC records where lawful and contractually usable.
- AI natural-language search that turns normal user requests into structured filters.
- A CRM that manages the full property + owner + motivation signal workflow.
- Compliance-safe outreach, including direct mail, email, manual calling, and later consented SMS.

## Canonical Strategy Docs

Start with these polished planning docs:

- [Master Plan](docs/strategy/MASTER_PLAN.md)
- [Public Records Engine](docs/strategy/PUBLIC_RECORDS_ENGINE.md)
- [Data and Unit Economics](docs/strategy/DATA_AND_UNIT_ECONOMICS.md)
- [Integrations and MLS](docs/strategy/INTEGRATIONS_AND_MLS.md)
- [Native App Roadmap](docs/strategy/NATIVE_APP_ROADMAP.md)
- [Compliance and Messaging](docs/strategy/COMPLIANCE_AND_MESSAGING.md)
- [Repo Cleanup Status](docs/strategy/REPO_CLEANUP_STATUS.md)

## First Engineering Goal

Do not build everything at once. Build one vertical slice:

```text
mock property/owner/public-record data
→ natural-language search parser
→ structured search results
→ lead profile
→ AI explanation
→ saved list
→ CRM task
```

## Launch Wedge

Start with a priority market, ideally Southern California / Los Angeles area:

```text
property/owner/equity base
+ NOD / foreclosure
+ probate
+ code violations
+ tax delinquency
+ FSBO/listing signals
+ AI search
+ CRM
+ skip tracing
+ direct mail/email/manual call tasks
```

Then expand to:

```text
BK / bankruptcy
divorce / dissolution and property-transfer signals
evictions
liens/judgments
permits
MLS/listing integrations
consented SMS
Android
API / enterprise
```
