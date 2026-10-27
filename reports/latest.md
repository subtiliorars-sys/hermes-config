# Model catalog audit

Checked: 2026-10-27T00:55:06.187367+00:00

Listing/pricing audit only; no inference calls, quality ranking, entitlement test or automatic routing changes.

- nous: 422 listed; 7 advertised zero-cost text tokens
- openrouter: 462 listed; 20 advertised zero-cost text tokens

| Config path | Provider | Model | Status |
|---|---|---|---|
| model | nous | openai/gpt-6-astra | listed |
| fallback_providers[0] | nous | google/gemini-4-argon | listed |
| fallback_providers[1] | nous | deepseek/deepseek-v4.1-flash | listed |
| fallback_providers[2] | nous | stepfun/step-3.7-flash:free | listed |
| fallback_providers[3] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| fallback_providers[4] | nous | poolside/laguna-xs-2.1:free | listed |
| fallback_providers[5] | nous | upstage/solar-pro4:free | missing-from-catalog |
| fallback_providers[6] | nous | tencent/hy3:free | missing-from-catalog |
| fallback_providers[7] | custom | qwen3:4b | local-not-checked |
| auxiliary.vision | nous | ornith/ornith-1.5-122b:free | listed |
| auxiliary.vision.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.compression | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.compression.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.compression.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.review | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.review.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.review.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.title_generation | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.title_generation.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.title_generation.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.curator | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.curator.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.curator.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.background_review | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.background_review.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.background_review.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.moa_reference | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.moa_reference.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.session_search | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.session_search.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.session_search.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| auxiliary.web_extract | nous | stepfun/step-3.7-flash:free | listed |
| auxiliary.web_extract.fallback_chain[0] | nous | reflection/beam-1.0-501b-a23b:free | listed |
| auxiliary.web_extract.fallback_chain[1] | nous | poolside/laguna-xs-2.1:free | listed |
| delegation | nous | openai/gpt-6-astra | listed |
| moa.presets.cost_optimized.aggregator | nous | openai/gpt-6-astra | listed |
| moa.presets.cost_optimized.reference_models[0] | nous | google/gemini-4-argon | listed |
| moa.presets.cost_optimized.reference_models[1] | nous | deepseek/deepseek-v4.1-flash | listed |
| moa.presets.cost_optimized.reference_models[2] | nous | stepfun/step-3.7-flash:free | listed |
| moa.presets.cost_optimized.reference_models[3] | custom | qwen3:4b | local-not-checked |
| moa.presets.hermes_free_first.aggregator | nous | stepfun/step-3.7-flash:free | listed |
| moa.presets.hermes_free_first.reference_models[0] | nous | stepfun/step-3.7-flash:free | listed |
| moa.presets.hermes_free_first.reference_models[1] | nous | upstage/solar-pro4:free | missing-from-catalog |
| moa.presets.hermes_free_first.reference_models[2] | nous | poolside/laguna-xs-2.1:free | listed |
| moa.presets.hermes_free_first.reference_models[3] | custom | qwen2.5:3b | local-not-checked |
| moa.presets.local_only.aggregator | custom | qwen3:4b | local-not-checked |
| moa.presets.local_only.reference_models[0] | custom | qwen3:4b | local-not-checked |
