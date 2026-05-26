# Duplicate File Cleanup Report

Prompt ID: `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01`

## Summary

- Duplicate-looking files matching `* 2.*` found before cleanup: 180.
- Additional duplicate-looking copy artifacts found after the requested pattern scan: 3 exact duplicate files (`qa_fixtures/docs/.gitkeep 2`, `scripts/agent 2`, `reports/sessions/.gitkeep 2`) and 2 empty duplicate directories.
- Exact duplicate files removed: 182 files plus 2 empty duplicate directories.
- Unique duplicate files quarantined: 1.
- Remaining `* 2.*` / `* 2` artifacts after cleanup: none outside ignored quarantine.

## Quarantined Unique Content

| duplicate | counterpart | classification | action | notes |
|---|---|---|---|---|
| `agent/tools/secrets 2.py` | `agent/tools/secrets.py` | `duplicate_with_unique_content_needs_merge` | moved to ignored quarantine at `docs/reconciliation/duplicate_file_quarantine/agent__tools__secrets_2.py` | Older source copy differed only in fake secret fixture literals. Current counterpart keeps safer fake-secret placeholders. Do not stage quarantined content without manual review. |

## Exact Duplicate Removals

| removed duplicate | original counterpart | sha256 |
|---|---|---|
| `agent/commands/intent_index 2.py` | `agent/commands/intent_index.py` | `36c08847f5d6d08b15acb2fa2406358601d35c27b290b9efdd85df677a0bae55` |
| `agent/commands/models 2.py` | `agent/commands/models.py` | `dcebafc53b54a82b877daf2f91603da7274b29a49e2b9f3099b5397d979fa90b` |
| `agent/dogfood/suites 2.py` | `agent/dogfood/suites.py` | `d348203ae2c6a4452d9aa332eec8d2d5362ed30d252ffb377416b131f78b702d` |
| `agent/forums/__init__ 2.py` | `agent/forums/__init__.py` | `bf6153bc8d2203f273af3ee0200879e21cec6e7f1385ded2910315e6b1dfec15` |
| `agent/forums/provider_status 2.py` | `agent/forums/provider_status.py` | `1287f2c24006f52d45c728f7df106607e6e22d175c356e89517642f952659544` |
| `agent/language/__init__ 2.py` | `agent/language/__init__.py` | `06f6cabc5bcaf91893bd5dfaceb2d7f42bf51d3595a9654bf24579e95c41b257` |
| `agent/media/__init__ 2.py` | `agent/media/__init__.py` | `94f9e4fb7faa80de36258ec431d42085a1d533ec6b2b88705fe058098bf21064` |
| `agent/messaging/handoff_payloads 2.py` | `agent/messaging/handoff_payloads.py` | `6be741ed4e6c67da7f833f7e957fd74e67fe95f2798e914653ca18e629342259` |
| `agent/messaging/inbound 2.py` | `agent/messaging/inbound.py` | `d0d205b6ccb2109f9f99355bae59c8261dc8f11e018fb5abb00a19f2942dca31` |
| `agent/native_skills/inspector 2.py` | `agent/native_skills/inspector.py` | `743ddd3000726579819615caa53d49f4e8ff9d44c56f3b4be2e3ff442b53a2ca` |
| `agent/native_skills/loader 2.py` | `agent/native_skills/loader.py` | `5b3d6db1e028364db4a5b96ac59baaf50c4a4c082808cf426831f23b11637d5f` |
| `agent/native_skills/roots 2.py` | `agent/native_skills/roots.py` | `c51108ec339118f333a24b0fd32fb9fa8d6f9cef3210d0bc3624ccdaaef5a258` |
| `agent/natural_language/preview 2.py` | `agent/natural_language/preview.py` | `ae81b6517d7c2a00fe207879215cf9467bc0dc448b322ca6d3ef74a41d3c60a4` |
| `agent/performance/baselines 2.py` | `agent/performance/baselines.py` | `469a892dbd5bdd9b854de5db9959046bedfc6af47cef089159cd1fbd99401dc9` |
| `agent/performance/patch_planner 2.py` | `agent/performance/patch_planner.py` | `ea40854b00deb4122dac5747d1886245d61cac963a0ef7911096d998e0128e0b` |
| `agent/platforms/app_bridge/errors 2.py` | `agent/platforms/app_bridge/errors.py` | `47a58cda6bbd46dc06e4757547aad5f62867afdf6d3b8d0f97dd195d9be38ce5` |
| `agent/platforms/app_bridge/models 2.py` | `agent/platforms/app_bridge/models.py` | `29307861d2bb58fe350ef0c497e28987908497f013c9cae37b23ccb639f157e6` |
| `agent/platforms/paths 2.py` | `agent/platforms/paths.py` | `44323b0701568615fc47880a98c759a3e6fad52250bacac8fa915ab09bb17f71` |
| `agent/platforms/web_bridge/__init__ 2.py` | `agent/platforms/web_bridge/__init__.py` | `b7daff1004d4d1f52447429cc36a3e9c727d263d30edb6af8370456608393166` |
| `agent/platforms/web_bridge/capabilities 2.py` | `agent/platforms/web_bridge/capabilities.py` | `5d16bb4fd8f97affc9ed3b5863452563c1af50e42a03252845db084ffc4e9fa4` |
| `agent/qa/api_models 2.py` | `agent/qa/api_models.py` | `c233fedcede728c7633271a7bc2a500967c04ff3da3ffbd0abb3a67645014517` |
| `agent/qa/safety 2.py` | `agent/qa/safety.py` | `940342496c7993b12ea805abb9e3dbb11ae7ebe914f62a7a55a8ad2a382bc3e4` |
| `agent/runtime/kernel 2.py` | `agent/runtime/kernel.py` | `467cb1d3eef30284de409f5b1c5d598dcae29710748a472936bc6206d73e011a` |
| `agent/runtime/state 2.py` | `agent/runtime/state.py` | `c10cfb01b8d80a6839186913c98f96bc49f5a7c44e83c8737b1f8332b9cef86e` |
| `agent/runtime/workflow_runner 2.py` | `agent/runtime/workflow_runner.py` | `06f447e7b218387c203248e3ba0fbbe888fca17c76fc3a2a0b460de0be9843ac` |
| `agent/sandbox/__init__ 2.py` | `agent/sandbox/__init__.py` | `0a718115bfc0b11788d4af15f24d2790f55c388f54bc189631eb7c674c8dd689` |
| `agent/sandbox/base 2.py` | `agent/sandbox/base.py` | `159dbe52194b799ee47335d8cfab9493ee42493eb665445a7333c2bbde581813` |
| `agent/sandbox/models 2.py` | `agent/sandbox/models.py` | `324387910ede482c5bc923e1c63a8eff6c76a6706d8c773d866566afb3935bf6` |
| `agent/secrets/sources 2.py` | `agent/secrets/sources.py` | `8ffc38225a75c0eaa8d569922d859a75a4b45f75c307b770594fa63097a85097` |
| `agent/session_logs/reviewer 2.py` | `agent/session_logs/reviewer.py` | `55c238b3550dde06e3996bf74f0a428a5d9386257eed1863939bfc160b5ce240` |
| `agent/tools/forums/reddit 2.py` | `agent/tools/forums/reddit.py` | `4d127e4ef9bfcdd51b3aa35ed228ab96e02ea19738687b747fddea3397c57c3b` |
| `agent/web_acquisition/models 2.py` | `agent/web_acquisition/models.py` | `fcd19ae90eb69da10b142a0476469235364d38718452d3de48ec1fa84dce161f` |
| `agent/web_acquisition/policy 2.py` | `agent/web_acquisition/policy.py` | `82295b0fe659d2ac1d601a7cc9aca02a2d4e9437d37fc5801054c5db20685a4d` |
| `agent/web_acquisition/robots 2.py` | `agent/web_acquisition/robots.py` | `18c1b7b2b1c26b7acd60c135446c81e91bb8c3940599cf56c6d8d376008b880d` |
| `agent/web_acquisition/search/base 2.py` | `agent/web_acquisition/search/base.py` | `a7e90c485504b82c5344c49b1ec33fbe33fac84c23b481c598d6da361f9f26f7` |
| `docs/ARCHITECTURE_PRINCIPLES 2.md` | `docs/ARCHITECTURE_PRINCIPLES.md` | `66ca416a58b418f4ec67720390150e68eff2cdd7b0dfd5717ca19e99d1f3e67c` |
| `docs/BUILD_PROVENANCE 2.md` | `docs/BUILD_PROVENANCE.md` | `846e7db38bdcc07a9c70959c1df3345a6951d107538aa4fc666182a07b64eeb2` |
| `docs/HANDOFF_TO_CHATGPT 2.md` | `docs/HANDOFF_TO_CHATGPT.md` | `485d98ba624d112681236e1cbf51038a25b061e44d36c89c50f0e25904a04f01` |
| `docs/MODEL_MIGRATION_GUIDE 2.md` | `docs/MODEL_MIGRATION_GUIDE.md` | `0ede11ae76ed803a5b8cb59cf12ed1d911b799b80440e54e4df31a65df1c5e79` |
| `docs/autonomy/AUTONOMY_RISK_MODEL 2.md` | `docs/autonomy/AUTONOMY_RISK_MODEL.md` | `c9a4203860bf3a032ae92bf42362707c2d648d1927cd3c9a59efc8d5e9ee21dc` |
| `docs/autonomy/CROSS_SESSION_CONTINUITY 2.md` | `docs/autonomy/CROSS_SESSION_CONTINUITY.md` | `5319591b2573b429c9f1ee6dd585e1cb792d5412ce3aa779b87ba6f9d6d35ff6` |
| `docs/autonomy/HERMES_FEATURE_COMPARISON 2.md` | `docs/autonomy/HERMES_FEATURE_COMPARISON.md` | `c472f64eea44f7578b465fd18a6b0ac3239d43e240cf44ab11c407a333b088fd` |
| `docs/autonomy/HERMES_INSPIRED_MATURITY_REVIEW 2.md` | `docs/autonomy/HERMES_INSPIRED_MATURITY_REVIEW.md` | `dd3aab4969915a3a74d6b060d9649bd6083ae41d83fa041b66a73d8e01fcb637` |
| `docs/autonomy/HERMES_INSPIRED_RELEASE_GATE 2.md` | `docs/autonomy/HERMES_INSPIRED_RELEASE_GATE.md` | `c0978f7f55465045edf3cf111470894c397c76d6a6219918a966662ff2c781fd` |
| `docs/autonomy/HIGH_RISK_AUTONOMY_GATES 2.md` | `docs/autonomy/HIGH_RISK_AUTONOMY_GATES.md` | `137cb91afe7904a7dcc96e5e762bec659cd898a8f23b3421e876ef3115daab4d` |
| `docs/autonomy/MODEL_SWITCHING 2.md` | `docs/autonomy/MODEL_SWITCHING.md` | `bc950121f42161511553138a7fc6564e7d3a701f2d563884ea61181773ad57a6` |
| `docs/autonomy/SAFE_AUTONOMY_DOGFOOD_RUNBOOK 2.md` | `docs/autonomy/SAFE_AUTONOMY_DOGFOOD_RUNBOOK.md` | `3ed28e0dc41f19012b7f25103082cf7e2be50524e50f2d97cc69177422cb3e6a` |
| `docs/autonomy/SAFE_AUTONOMY_ROADMAP 2.md` | `docs/autonomy/SAFE_AUTONOMY_ROADMAP.md` | `abfb22eff80c83fffe992c07b4398d02080606ec7910c43a797c5dd9d434b9ed` |
| `docs/autonomy/SANDBOX_BACKEND_ABSTRACTION 2.md` | `docs/autonomy/SANDBOX_BACKEND_ABSTRACTION.md` | `b0eaa5bc278e8e97a11da909a0d9b658c0c8d07378ea6f4d1a39b398fa377af9` |
| `docs/autonomy/SANDBOX_POLICY 2.md` | `docs/autonomy/SANDBOX_POLICY.md` | `cff508b377ac44bf48160a2bc2383cf2f5aa0b408f3c721cb9f1295876656341` |
| `docs/autonomy/SCHEDULED_ACTION_GATES 2.md` | `docs/autonomy/SCHEDULED_ACTION_GATES.md` | `2cb7c86c4292919189969611408faf67d5c457332bf2a4a3ef8393f2603c75f7` |
| `docs/autonomy/SCHEDULER_UX 2.md` | `docs/autonomy/SCHEDULER_UX.md` | `28c5df5ea3c13890c67e5b79d1c949031bbf6cb481789d0188fc32af5e1df3be` |
| `docs/autonomy/SKILL_CREATION_FROM_REPEATED_TASKS 2.md` | `docs/autonomy/SKILL_CREATION_FROM_REPEATED_TASKS.md` | `b2e9bedb609c40b493bb4350eb9626d5956277285b8faed5a63a4498f08c1a97` |
| `docs/autonomy/SKILL_IMPROVEMENT_FROM_EXPERIENCE 2.md` | `docs/autonomy/SKILL_IMPROVEMENT_FROM_EXPERIENCE.md` | `2d805815905997b11dbebeea415398ab82297e501b18fdc17c5a8af5bb6104b3` |
| `docs/autonomy/SUBAGENT_ISOLATION 2.md` | `docs/autonomy/SUBAGENT_ISOLATION.md` | `15fc07cf801d666695d91b5bd861462f2e89669d33112ecc0864d1f62991cc20` |
| `docs/autonomy/SUBAGENT_PROFILES 2.md` | `docs/autonomy/SUBAGENT_PROFILES.md` | `6a8e8182c96ccd6b89e3f8d5da65011c41d928db1354449a3ce54d52c514d9ff` |
| `docs/autonomy/UNAUTHORIZED_BYPASS_POLICY 2.md` | `docs/autonomy/UNAUTHORIZED_BYPASS_POLICY.md` | `2bf2d460afda80749b391af268cfc91ce3e03a070ef52115094a77852ea5fa77` |
| `docs/cloneability/CLONEABILITY_MATURITY_REVIEW 2.md` | `docs/cloneability/CLONEABILITY_MATURITY_REVIEW.md` | `0d023dbf1b15029c65173b9006469deddd71d2ae55fb3b5ae444139522fcb3d0` |
| `docs/cloneability/CLONEABILITY_RELEASE_GATE 2.md` | `docs/cloneability/CLONEABILITY_RELEASE_GATE.md` | `324062092df356a04cc4ff464ec2d0615a1456a341894fea160786265bcdf2a9` |
| `docs/decisions/apple_messages_strategy 2.md` | `docs/decisions/apple_messages_strategy.md` | `f2d9172ab9ad345b68847d9f75f7dbbb8c791545a042263fc3295bd94e0a1798` |
| `docs/decisions/incoming_message_strategy 2.md` | `docs/decisions/incoming_message_strategy.md` | `5657b6da34d886586d35523a500c133b3210dd536ffd5f47dbcc22142533e5e5` |
| `docs/decisions/natural_language_command_understanding 2.md` | `docs/decisions/natural_language_command_understanding.md` | `437f222fbde3b3780839de02a9b9366afbe30ebf225979c976382a62f59dd49f` |
| `docs/media/AUDIO_MUSIC_GENERATION_STRATEGY 2.md` | `docs/media/AUDIO_MUSIC_GENERATION_STRATEGY.md` | `7f940b6d601706984622659abbb9a73eed9525e9d40f0029e538508a05514fca` |
| `docs/media/CREATIVE_MEDIA_GENERATION_TRACK 2.md` | `docs/media/CREATIVE_MEDIA_GENERATION_TRACK.md` | `46b7e0c41cb0253bab0d41565a3ef8988b9df587af85406549b6f5f1c56ce221` |
| `docs/media/CREATIVE_MEDIA_MATURITY_REVIEW 2.md` | `docs/media/CREATIVE_MEDIA_MATURITY_REVIEW.md` | `c5154902d8e7846f75c2b4c5ec29362e7cc6107672643d72784200ef8786948d` |
| `docs/media/CREATIVE_MEDIA_RELEASE_GATE 2.md` | `docs/media/CREATIVE_MEDIA_RELEASE_GATE.md` | `b720a614b70b05839b575a6659c2ffd9b21ec94ef2b0bdc73c71f30e4a960140` |
| `docs/media/IMAGE_GENERATION_STRATEGY 2.md` | `docs/media/IMAGE_GENERATION_STRATEGY.md` | `e37b060b0ce4e9bb6b8ed324dd4548afaa10dc706e25f1435bf39ac6ab42bb00` |
| `docs/media/MEDIA_ASSET_MANAGER 2.md` | `docs/media/MEDIA_ASSET_MANAGER.md` | `79ab454726a2f423777fe3235da73068ee78e001c5312d6ec4941a3f1552620a` |
| `docs/media/MEDIA_ASSET_POLICY 2.md` | `docs/media/MEDIA_ASSET_POLICY.md` | `16e166ebc6ef74c1bd5951ef4c24ea651dce1bde276c850afab4daaac6279587` |
| `docs/media/MEDIA_CONSENT_POLICY 2.md` | `docs/media/MEDIA_CONSENT_POLICY.md` | `03ccd7cec9cd178b7edd727481695725fcfe6fb7feab2fbb96b6ff993e256177` |
| `docs/media/MEDIA_COPYRIGHT_AND_LICENSE_POLICY 2.md` | `docs/media/MEDIA_COPYRIGHT_AND_LICENSE_POLICY.md` | `4de98a78ac69c8a431fe5f559377ed8847504266e7292db308db0829c5ab1831` |
| `docs/media/MEDIA_DOGFOOD_RUNBOOK 2.md` | `docs/media/MEDIA_DOGFOOD_RUNBOOK.md` | `635070e472b5b77baea8c26d21097ac55d89a6df0621edc17b0c6ea0acfbe9d7` |
| `docs/media/MEDIA_LICENSE_POLICY 2.md` | `docs/media/MEDIA_LICENSE_POLICY.md` | `c1250df892d7e87bc19d3e1f1e2e68172d08b4f1b1f3e82176abe8062f7da744` |
| `docs/media/MEDIA_PROMPT_SAFETY 2.md` | `docs/media/MEDIA_PROMPT_SAFETY.md` | `35745857a14ca4b84454b73f7ba0dc5d93cb5b2f958afc6c8c94fd7c78709961` |
| `docs/media/MEDIA_PROVIDER_REGISTRY 2.md` | `docs/media/MEDIA_PROVIDER_REGISTRY.md` | `ebf7c74060eee5c067376178004be6e63c6931a101741d3e8751c3645ed22fc0` |
| `docs/media/MEDIA_PROVIDER_STRATEGY 2.md` | `docs/media/MEDIA_PROVIDER_STRATEGY.md` | `6ecda20526632b90a516cb05b419816d331a7e03d62370ec04190baca675e323` |
| `docs/media/MEDIA_RISK_MODEL 2.md` | `docs/media/MEDIA_RISK_MODEL.md` | `41ddd49c02e872bc0f39931bd2ecdb279a02b5a02b14665866b3e3dc6e7e02c6` |
| `docs/media/MEDIA_SAFETY_POLICY 2.md` | `docs/media/MEDIA_SAFETY_POLICY.md` | `3768e85c2f75ce2347dc8c04787ddbb775f65b67805389bfb89af33370d499dd` |
| `docs/media/MEDIA_WORKFLOW_COMMANDS_AND_NL_ROUTING 2.md` | `docs/media/MEDIA_WORKFLOW_COMMANDS_AND_NL_ROUTING.md` | `dff86fb26e17f67bf23ba9c7af57977535dab94aec6c963569e55d35f41ef50e` |
| `docs/media/THUMBNAIL_SOCIAL_CREATIVE_WORKFLOWS 2.md` | `docs/media/THUMBNAIL_SOCIAL_CREATIVE_WORKFLOWS.md` | `76294efc33305e994703c17ff190cf20a5b0cf28a62a018a0fd6edd619365de5` |
| `docs/media/TTS_VOICE_GENERATION_STRATEGY 2.md` | `docs/media/TTS_VOICE_GENERATION_STRATEGY.md` | `cd3e90a849617e6fbb4f6b65707f5cfa1ad9bc23161aad9be09b886c1c8e12f0` |
| `docs/media/VIDEO_GENERATION_STRATEGY 2.md` | `docs/media/VIDEO_GENERATION_STRATEGY.md` | `e1ca2b088c41f4a5d64ae5a99bdc6574a3a96c319294995e43a400efc2e1e729` |
| `docs/media/VOICE_CONSENT_POLICY 2.md` | `docs/media/VOICE_CONSENT_POLICY.md` | `845ae9498bc223df63559f3423d1ec29f2cd7f20a4ec7e684d76541de7873bfd` |
| `docs/reconciliation/ARTIFACT_AND_GIT_HYGIENE_RECONCILIATION 2.md` | `docs/reconciliation/ARTIFACT_AND_GIT_HYGIENE_RECONCILIATION.md` | `9705c6db5c8d47519f69eb1c18f4aeee1f51b30b3915094a1b2ac154fcd7a653` |
| `docs/reconciliation/ARTIFACT_TRACKING_DECISION 2.md` | `docs/reconciliation/ARTIFACT_TRACKING_DECISION.md` | `31f3903fb271bd2040822f1b357b4c80390380e1955ca08bbfd97b69eec47724` |
| `docs/reconciliation/CAPABILITY_MANIFEST_RECONCILIATION 2.md` | `docs/reconciliation/CAPABILITY_MANIFEST_RECONCILIATION.md` | `8d9e190bc0ccfa331562523a2a19137f69105a412dc87dcc94230e363b6dd8a6` |
| `docs/reconciliation/CLEAN_RELEASE_CANDIDATE_BOUNDARY_PLAN 2.md` | `docs/reconciliation/CLEAN_RELEASE_CANDIDATE_BOUNDARY_PLAN.md` | `49f3668e3b3446f6c7955c059601597cb70fafb2365e18be50336e9c2d999f7f` |
| `docs/reconciliation/COMMAND_REGISTRY_RECONCILIATION 2.md` | `docs/reconciliation/COMMAND_REGISTRY_RECONCILIATION.md` | `d156191aa9bfce64a91aefec0af1bf5a2a8f79f24e702c721aefb024ab57147b` |
| `docs/reconciliation/CURRENT_REPO_STATE_SNAPSHOT 2.md` | `docs/reconciliation/CURRENT_REPO_STATE_SNAPSHOT.md` | `8a65d2479501584c35739fc3fae8d6c1e2e49322c5865f446bfb125178aa72a6` |
| `docs/reconciliation/DOCS_WIRING_RECONCILIATION 2.md` | `docs/reconciliation/DOCS_WIRING_RECONCILIATION.md` | `bcd9a8f88cbb1f9b64d1e47ac8119300b44ea63b80807855608b5961d8f51cb7` |
| `docs/reconciliation/FEATURE_AND_MATURITY_RECONCILIATION 2.md` | `docs/reconciliation/FEATURE_AND_MATURITY_RECONCILIATION.md` | `883c39efc334d29c8ed35505fd8a054a05bf11892865e06e8505615de58b3f93` |
| `docs/reconciliation/PROMPT_TRACKER_RECONCILIATION 2.md` | `docs/reconciliation/PROMPT_TRACKER_RECONCILIATION.md` | `7efaacf169c8f0dfadb70effe0d01750feac52e1b99b7d1656ba1ef6a6e6a308` |
| `docs/reconciliation/QA_TEST_DOGFOOD_RECONCILIATION 2.md` | `docs/reconciliation/QA_TEST_DOGFOOD_RECONCILIATION.md` | `95459433650182c4f4029280d5bc5424997fae1843b31f4701cd22494f9abd1b` |
| `docs/reconciliation/SOURCE_OF_TRUTH_HIERARCHY 2.md` | `docs/reconciliation/SOURCE_OF_TRUTH_HIERARCHY.md` | `dc12e18b623a0b86d20aa1acfcc84677564794d9a105c732782de5afe410a6af` |
| `docs/reconciliation/SOURCE_TRUTH_RECONCILIATION_FINAL_REPORT 2.md` | `docs/reconciliation/SOURCE_TRUTH_RECONCILIATION_FINAL_REPORT.md` | `cdaa99cb00093acf17ec6c8dc1f80cd76e77df8368095919cf40335db2a4ae60` |
| `docs/templates/nl_regression_case_template 2.yaml` | `docs/templates/nl_regression_case_template.yaml` | `66172387fedcf9710b48fe1619989b905909e8dfeff5eb546c20547a914786d2` |
| `docs/templates/skill_profile_template 2.yaml` | `docs/templates/skill_profile_template.yaml` | `829d222914a5dd1766abff7c566a6012cdb55dac7dd9426ec1d79619409562f6` |
| `docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY 2.md` | `docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md` | `05e56d2b672b0f9af88887880fa7d3ccf5a847e839e071b7819fc44499c8a15e` |
| `docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY 2.md` | `docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md` | `2cb8a4037fff1f6348e48bdd5a639e1e8eeab0865b9e9c83c8d6fd9dbd60e917` |
| `docs/web/BLOCKED_SOURCE_POLICY 2.md` | `docs/web/BLOCKED_SOURCE_POLICY.md` | `5c31dce5b6c8bded43c7c94d50b1d307e584e3c45760f8a66f5cb1bf61de4ee9` |
| `docs/web/CITATION_POLICY 2.md` | `docs/web/CITATION_POLICY.md` | `a07b1280acd3c95104ecc57c2965c06ec2298d3a0b8e3d05d0a5cf61e6010133` |
| `docs/web/DEEP_SCAN_POLICY 2.md` | `docs/web/DEEP_SCAN_POLICY.md` | `f052a75005cf25664340fcf5d61112a2ce97346e42718948216991fd2c61c75a` |
| `docs/web/FEEDS_AND_SITEMAPS 2.md` | `docs/web/FEEDS_AND_SITEMAPS.md` | `34e7dbf182dbe3f99ac50146c42dc013e122d62a9a883264bbf66f3be8e23303` |
| `docs/web/FIRST_PARTY_TESTING_POLICY 2.md` | `docs/web/FIRST_PARTY_TESTING_POLICY.md` | `254f5178676f49b2cdf453aa53387f0b2772110dba626241d07b8a3ab7e22184` |
| `docs/web/INTERNET_DOGFOOD_RUNBOOK 2.md` | `docs/web/INTERNET_DOGFOOD_RUNBOOK.md` | `b05f825f0164008179557265ee23e08920d8bdb6f2f1e63647704664cc4b13ea` |
| `docs/web/INTERNET_PROVIDER_STRATEGY 2.md` | `docs/web/INTERNET_PROVIDER_STRATEGY.md` | `9f289becd0e2aa57324efe04045efa315d427686a278f7b280a6e6f5a17d119b` |
| `docs/web/INTERNET_ROUTING_POLICY 2.md` | `docs/web/INTERNET_ROUTING_POLICY.md` | `30988f6d741f0c9f52ce85e9f4fbb54f1b07c398c23e72ad6a18ee5b41cbc211` |
| `docs/web/LOCAL_WEB_INDEX 2.md` | `docs/web/LOCAL_WEB_INDEX.md` | `09816e413ad745aaca6a444a257526a64e9dae94c9153649de2917f0033cccf6` |
| `docs/web/OFFICIAL_API_CONNECTORS 2.md` | `docs/web/OFFICIAL_API_CONNECTORS.md` | `9a44930aaec4e0b6f0b1057194ad8689cf7c9a12be5b7a881b5c9c327f8775d4` |
| `docs/web/PROVIDER_SELECTION 2.md` | `docs/web/PROVIDER_SELECTION.md` | `a3104beec0a69c6d05e9ea94c4bc693d86011d95a0777e93c6301d716021de43` |
| `docs/web/ROBOTS_AND_RATE_LIMITS 2.md` | `docs/web/ROBOTS_AND_RATE_LIMITS.md` | `9adb28b9e0801514a3bb9592414e47e35e089ab935a331f6547b9a8cba6dcdc9` |
| `docs/web/SAFE_FETCH_AND_EXTRACTION 2.md` | `docs/web/SAFE_FETCH_AND_EXTRACTION.md` | `377369d7cd83817b862060ef09d156b312d6fbcd180d5e282554214060fa085a` |
| `docs/web/SEARCH_PROVIDER_REGISTRY 2.md` | `docs/web/SEARCH_PROVIDER_REGISTRY.md` | `cca968c45b76bdec5032c3a36862f9a97b0d6af8a8639ecd4d7352e1b3e03ee7` |
| `docs/web/SOURCE_GROUNDED_RESEARCH 2.md` | `docs/web/SOURCE_GROUNDED_RESEARCH.md` | `32eae4c19026e957fa14510e263c44e5564c53927074dfa8bea2fc82fefdedf6` |
| `docs/web/SOURCE_GROUNDING_REQUIREMENTS 2.md` | `docs/web/SOURCE_GROUNDING_REQUIREMENTS.md` | `1c6ff4e31c1bdd874691254d0285152079c989b92fc43dcd6179dff6b44536a9` |
| `docs/web/WEB_ACCESS_POLICY 2.md` | `docs/web/WEB_ACCESS_POLICY.md` | `33f67c30d5877cc2200f73299ad3a6152df8fe3a1f5ea42aa9a23f508ea0c828` |
| `docs/web/WEB_CACHE_POLICY 2.md` | `docs/web/WEB_CACHE_POLICY.md` | `c551ff2fe6e340abcc7edaaaffbc8624d61beaefe398be97baca8a718d0de98d` |
| `eval_cases/command_qa/command_qa 2.json` | `eval_cases/command_qa/command_qa.json` | `6cdd4417a546ada50d26fd83aa8ca44be492571b2e9c488974c4c23f071c7ef6` |
| `native_skills.lock 2.example` | `native_skills.lock.example` | `2a5a51268e17da89d5c44163b32cc6542945c7944d52d1699a2028bfff18811c` |
| `prompts/completed/BRAIN-05 2.md` | `prompts/completed/BRAIN-05.md` | `2b5e7746be8a4bef6a2f125b604d4327eee9858bc57aef4bcbe469b3da340050` |
| `prompts/completed/BRAIN-06 2.md` | `prompts/completed/BRAIN-06.md` | `4289240ab95e3d0119b8e6564f33527c0aac23e10e32e8840c625d94372abb48` |
| `prompts/completed/BRAIN-08 2.md` | `prompts/completed/BRAIN-08.md` | `dd3ffc1201b24d4f33cd36983ef8020a05421cf4e081311b47fe2f51f220f2dd` |
| `prompts/completed/CANON-02 2.md` | `prompts/completed/CANON-02.md` | `fb52801876882edb52b293c0f2cfbe62a42cf3c1a59b813c763e4b13619df4db` |
| `prompts/completed/CITATION-SOURCE-ATTRIBUTION 2.md` | `prompts/completed/CITATION-SOURCE-ATTRIBUTION.md` | `1f38b2b8c5bac59f31d20fec14bb0805b0e194d891fc11738bd03fa0a92b8a79` |
| `prompts/completed/CODEBUG-02 2.md` | `prompts/completed/CODEBUG-02.md` | `26a58503c1fa61b24c4b5d5c818c83122f91c2d11bb9a85a71d429edb2604c65` |
| `prompts/completed/CODEBUG-03 2.md` | `prompts/completed/CODEBUG-03.md` | `4c724357baf7ffd6f85dec11d4ba5a582f960881a48ebdbe81f416f0fba14c99` |
| `prompts/completed/DNA-06 2.md` | `prompts/completed/DNA-06.md` | `af4f74be6bb746a05a59e181cc8a87e99540bc845e968d81d52cefbace506898` |
| `prompts/completed/EXTREV-01 2.md` | `prompts/completed/EXTREV-01.md` | `e714294aeb9655b5b37064d509c975cda5a784e737d6f0b778229b32ba2d311d` |
| `prompts/completed/HERMES-02 2.md` | `prompts/completed/HERMES-02.md` | `187636663787658ab2f210b8852aabc6ef44ab2f4ed7dc782b3a344196fe994a` |
| `prompts/completed/HERMES-08 2.md` | `prompts/completed/HERMES-08.md` | `daed04f4fd6547a1753eb5a5002118a88f557c0fc6f1e6522dffe83af1466a64` |
| `prompts/completed/HERMES-09 2.md` | `prompts/completed/HERMES-09.md` | `ebeef12761ad2a10f18887144dc4249eaa72c246100babac5effb6dd8bb9dc50` |
| `prompts/completed/HERMES-12 2.md` | `prompts/completed/HERMES-12.md` | `c12e36c99ff7e315f1dead356247c9a939ff260da8307849ce2ba2ecb8d8e08d` |
| `prompts/completed/INTERNET-DOGFOOD-EVAL-SUITE 2.md` | `prompts/completed/INTERNET-DOGFOOD-EVAL-SUITE.md` | `020f8f0598890325e73efb346099bcf5aff1a9acbc79e1e70fd3411e12d78790` |
| `prompts/completed/MACOS-MESSAGES-PROBE 2.md` | `prompts/completed/MACOS-MESSAGES-PROBE.md` | `1913403b743af5886395f65274af27c0ff7ae5eddbb2a4e38d356a255d6d028f` |
| `prompts/completed/MEDIA-10 2.md` | `prompts/completed/MEDIA-10.md` | `23451b906ca14e5b1a6596853dfe77863056e4daa89d14db471f066d72f3b125` |
| `prompts/completed/MEDIA-12 2.md` | `prompts/completed/MEDIA-12.md` | `c0b6b885e6fa550eb1e807f2e8689e70e6d72ffa34145a7e5a68dfd03296c34e` |
| `prompts/completed/MESSAGE-SAFETY-ACTION-CENTER 2.md` | `prompts/completed/MESSAGE-SAFETY-ACTION-CENTER.md` | `3aa4692bdc89b46f5431abdc247450287bd35ef0209d394cd685ecdc35305af0` |
| `prompts/completed/NATIVE-SKILLS-FOUNDATION 2.md` | `prompts/completed/NATIVE-SKILLS-FOUNDATION.md` | `7861f3388626a93a2d857ee764546183bc8e9fff07d3b5ec2ec9e16b79cb04ba` |
| `prompts/completed/ORCH-02 2.md` | `prompts/completed/ORCH-02.md` | `a1e61b546f242bf28351ca50c9e629f7f9b2af184bb7d569aba3e15c88ad53f4` |
| `prompts/completed/PERF-08 2.md` | `prompts/completed/PERF-08.md` | `1779c56b635f9d60d1ab8136089dad46df65692c2b07bf29034baf633adc85fc` |
| `prompts/completed/PERF-10 2.md` | `prompts/completed/PERF-10.md` | `e1b1571891f6492ca594eb6da30459328ebe1947b3e55f7d9907b08e4340fe0b` |
| `prompts/completed/QA-01 2.md` | `prompts/completed/QA-01.md` | `bea04117a1cdf0cf783b59a7a984050bd09aa0e5f8845c0adaac572e5b9a7786` |
| `prompts/completed/REDDIT-OAUTH-CONFIG-DOCTOR 2.md` | `prompts/completed/REDDIT-OAUTH-CONFIG-DOCTOR.md` | `ad0548681ff949077a93c630b47883cd2b904d7c5c2df3c2f73297dd5e2a7e8d` |
| `prompts/completed/REDDIT-SEARCH-WORKFLOWS 2.md` | `prompts/completed/REDDIT-SEARCH-WORKFLOWS.md` | `4224cff88a2679ff178897f6395cc12ecd3297ff7840a4fbbd59c1b4139183e8` |
| `prompts/completed/SKILL-06 2.md` | `prompts/completed/SKILL-06.md` | `b0694331aae272212844d84a9f67f7618a111a00f6faab8d7ca2ba1bdae37153` |
| `prompts/completed/SKILL-08 2.md` | `prompts/completed/SKILL-08.md` | `55adbe3b95fd81d3d5a4b2b5c72600c57e06bfbaf913e5247b69c42298f97da3` |
| `prompts/completed/TRACKER-HYGIENE-INDEXING-COMPACTION 2.md` | `prompts/completed/TRACKER-HYGIENE-INDEXING-COMPACTION.md` | `de895c4dd211fb40dcfa527f0a18c60cf3e1a0c23ce3ca57b870df2125d58a59` |
| `prompts/completed/WEB-CACHE-DEDUPE-INDEX 2.md` | `prompts/completed/WEB-CACHE-DEDUPE-INDEX.md` | `b2392bc5e6cb3fca4f7c9d87e86d5be819b3a337bbebb292d6cd114c7163eeef` |
| `prompts/completed/news-capability-manifest-provider-policy 2.md` | `prompts/completed/news-capability-manifest-provider-policy.md` | `28662380cd834bae1687e33e38e34205fb4d13746c002b91133bf7c8e5a5ad7e` |
| `prompts/completed/news-intelligence-roadmap 2.md` | `prompts/completed/news-intelligence-roadmap.md` | `e17ad7dbd81df48d1346ecd095b2f304df2d5bf3ad4af24b9b9b19a577ab6650` |
| `prompts/packs/ai-ecosystem-intelligence-v2.promptpack 2.md` | `prompts/packs/ai-ecosystem-intelligence-v2.promptpack.md` | `07dd4a9727d758e08caad3560be5f71531f1be252f60a2de358a6a578befd839` |
| `prompts/packs/brain-runtime-independence-v1 2.md` | `prompts/packs/brain-runtime-independence-v1.md` | `f380db38cb9c75932ec8336d08d55b557fc8206e6f751c381090a71789560698` |
| `prompts/packs/native-skill-system-hardening-v1.promptpack 2.md` | `prompts/packs/native-skill-system-hardening-v1.promptpack.md` | `9e93a729465e267594c403612f11f2fc559bf840301817f92fd76770d6d0f975` |
| `prompts/packs/prompt-tracker-maturity-v1 2.md` | `prompts/packs/prompt-tracker-maturity-v1.md` | `880d8d958ae4f973c08ea308e84d4d9747bf1114639074e99ed5397c1a5b558e` |
| `qa_fixtures/docs/report 2.md` | `qa_fixtures/docs/report.md` | `334fe2ab6967e61c8bdbf8171e76bf939d8499bb87ac17e578546582af75f20b` |
| `tests/brain/test_llama_cpp_inprocess_provider 2.py` | `tests/brain/test_llama_cpp_inprocess_provider.py` | `efa16d21944d221f772c83bc06fd7c9dbbb2f81397dac241bf4786f7a8b43702` |
| `tests/brain/test_mlx_provider_stub 2.py` | `tests/brain/test_mlx_provider_stub.py` | `bafb43e0ae1dcea799acd3a12c687280fba2fa06134b58369a2a6c2bc4ffafea` |
| `tests/brain/test_model_registry 2.py` | `tests/brain/test_model_registry.py` | `73d606569aa11bab22b56e66fae49ba6302e1a4c58012c2d775ca9b4bb915d38` |
| `tests/media/test_media_dogfood_eval 2.py` | `tests/media/test_media_dogfood_eval.py` | `4152183a370159485737a8a35aa149558ab39a92826bdc3b95553d5cb297d0fb` |
| `tests/media/test_media_models_registry 2.py` | `tests/media/test_media_models_registry.py` | `af65be58b0a7bdb7c1313851fa1c555118923f1cc3e84c1b6c351adfc5804f4d` |
| `tests/media/test_tts_strategy 2.py` | `tests/media/test_tts_strategy.py` | `b86ebf13984c26b46fa55253ca82a09e8f4fceac586790b0d892fc5dda856dc4` |
| `tests/native_skills/test_skill_manifest_schema 2.py` | `tests/native_skills/test_skill_manifest_schema.py` | `7b7a68629898f2e833b6126027f25c3efff2dc9ec2403c5cde8a6766c086f944` |
| `tests/native_skills/test_skill_provenance_lockfile 2.py` | `tests/native_skills/test_skill_provenance_lockfile.py` | `09f4f19d39668ee2d176e03c344f5a6cb2e94fef392622859aa6a38ff7077a76` |
| `tests/natural_language/test_nl_execution_plan_preflight 2.py` | `tests/natural_language/test_nl_execution_plan_preflight.py` | `1ee5c0a894dab454d7bbe8f4b54cefae1155964cf0c5380264e6ed7b9baf12f7` |
| `tests/qa/test_qa_dashboard 2.py` | `tests/qa/test_qa_dashboard.py` | `9b63fd176843678cbc3401ae04241bd98ff239fed23b15f0c2a80f6e23c7a0dc` |
| `tests/runtime/test_event_bus 2.py` | `tests/runtime/test_event_bus.py` | `81754ca6dbef5b04055a9f19f19b97dbcc4355de5102512a47ee53fdfd9d8f54` |
| `tests/runtime/test_runtime_cli 2.py` | `tests/runtime/test_runtime_cli.py` | `51ccd64ac04808719fe62adb3d74d63feebf44d074393134c01bb7a0559c2a63` |
| `tests/runtime/test_runtime_kernel 2.py` | `tests/runtime/test_runtime_kernel.py` | `de30eab3d4b69d9a0438966b1d6786d2591089968dcc2e15f3efe9224e269096` |
| `tests/runtime/test_scheduler_policy 2.py` | `tests/runtime/test_scheduler_policy.py` | `d4a68a1c0b4ef96334b5b43ffabaac8f212e8a4158f6ce7edb89d4cccf3f7f61` |
| `tests/secrets/test_secrets_policy_docs 2.py` | `tests/secrets/test_secrets_policy_docs.py` | `805bc203481a34933b9cc5a6f0045d1b05e488317aa964daecf19395c873fa7c` |
| `tests/test_creative_media_docs 2.py` | `tests/test_creative_media_docs.py` | `59f9396e76e5cbf73e6abdc07b87c4472c006ca926f3f32845e0b839046b35f6` |
| `tests/test_forum_provider_registry 2.py` | `tests/test_forum_provider_registry.py` | `5fcf168ea264b18c31800639c189f83ebf47cb4b146147e562b412eb08aca669` |
| `tests/test_ios_compose_bridge 2.py` | `tests/test_ios_compose_bridge.py` | `45b48078135e9d793ca7c9c11ebd9a764e61f5e1b72169b67d5e1d483266ec3a` |
| `tests/test_official_api_connectors 2.py` | `tests/test_official_api_connectors.py` | `90bfc43c829a1ea3801a01de69c63a707c6e8ecc218e25a88368bfe0a180d8d9` |
| `tests/test_pdf_documents 2.py` | `tests/test_pdf_documents.py` | `b9a9800bcf43e3e77244bcad99d09c867ea9e01db652a82b416687cd10104ed5` |
| `tests/test_privacy_center 2.py` | `tests/test_privacy_center.py` | `46a1a9c1903a4fe4c3c66609a947ebbe08724fd939732dd56f11a90e1589f3d2` |
| `tests/test_reddit_provider_policy 2.py` | `tests/test_reddit_provider_policy.py` | `47adbd7e31e0c6501e6f8bab79bc846318d221a5724375527d069b1d334bca69` |
| `tests/test_startup_ergonomics 2.py` | `tests/test_startup_ergonomics.py` | `a589522edbbc991c2b543a04ad5d174eea337293d7f9960693cf7c17eaa4c829` |
| `tests/test_web_acquisition 2.py` | `tests/test_web_acquisition.py` | `4683e5288c4220c017af5fdcfcac73162fe45cd838c8e0040258aaac0355f0b7` |
| `qa_fixtures/docs/.gitkeep 2` | `qa_fixtures/docs/.gitkeep` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `scripts/agent 2` | `scripts/agent` | `32a5ad6d38dc32b36fcb87962a08915cc7fe33aa65cfb90947dce68b4ef04119` |
| `reports/sessions/.gitkeep 2` | `reports/sessions/.gitkeep` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `docs/media/providers 2/` | `docs/media/providers/` | empty duplicate directory |
| `docs/web/providers 2/` | `docs/web/providers/` | empty duplicate directory |

## Cleanup Policy

- Removed only byte-for-byte duplicates or empty duplicate directories with existing counterparts.
- Did not delete the one differing source copy; it was quarantined and ignored for manual review.
- Did not run AIHUB, import AIHUB, execute queued feature prompts, merge unrelated histories, rebase, or force push.

## Follow-Up Scan

Prompt ID: `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01`

- Date: 2026-05-26 UTC / 2026-05-26 PDT.
- Command: `find . -name '* 2.*' -not -path './.git/*' -not -path './.venv/*' -not -path './__pycache__/*' | sort`
- Result: no matching duplicate copied files remain outside ignored paths.
- No additional files were removed or quarantined in the follow-up pass.
