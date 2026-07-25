# Model Migration: Gemini 1.5 Pro to gemini-flash-latest

**Date:** 25 July 2026
**Status:** Applied

## Summary

The project documentation specifies Google Gemini 1.5 Pro for question
answering, quiz generation, summarization, and learning recommendations. That
model has been retired by Google and is no longer callable. The implementation
now uses `gemini-flash-latest`.

## What Happened

Calling the documented model with a valid API key returns HTTP 404:

```
404 models/gemini-1.5-pro is not found for API version v1beta,
or is not supported for generateContent.
```

Because the AI client treats any provider failure as a signal to use local
fallback output, this did not surface as an error. The application continued to
answer requests using deterministic fallback text while `/health` still reported
the provider as configured. The failure was therefore silent, and was only
identified by inspecting the `model_used` value on stored responses.

## Models Evaluated

| Model | Result |
| --- | --- |
| `gemini-1.5-pro` | 404 - retired |
| `gemini-2.5-pro` | 429 - quota exceeded on this account tier |
| `gemini-2.0-flash` | 429 - quota exceeded on this account tier |
| `gemini-2.0-flash-lite` | 429 - quota exceeded on this account tier |
| `gemini-pro-latest` | 429 - quota exceeded on this account tier |
| `gemini-2.5-flash` | 404 - not available to new users |
| **`gemini-flash-latest`** | **working** |
| `gemini-flash-lite-latest` | working |

## Resolution

`GEMINI_MODEL` is set to `gemini-flash-latest`. All five educational features
were re-verified against the running application and confirmed to return
provider-generated output, with `model_used` recorded as `gemini-flash-latest`
on each stored response.

## Impact on the Codebase

None. The model name is read from the `GEMINI_MODEL` environment variable in
`backend/app/core/config.py` and consumed by
`backend/app/ai_modules/features/ai_client.py`. No application logic depends on
a specific model name, so the migration required a single configuration change.
Switching to a different model in future requires editing `.env` only.

## Note on Quota

Several models returned HTTP 429 on the development account. When a provider
call fails for any reason, including quota exhaustion, the application returns
local fallback text rather than an error response. The `model_used` field on each
response distinguishes provider output from fallback output, and is the
recommended way to confirm that the provider is genuinely serving requests.
