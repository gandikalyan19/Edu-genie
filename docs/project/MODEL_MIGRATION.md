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
| `gemini-2.5-pro` | 429 - free tier request limit is 0 |
| `gemini-2.0-flash` | 429 - free tier request limit is 0 |
| `gemini-pro-latest` | 429 - free tier request limit is 0 |
| `gemini-3-pro-preview` | 429 - free tier request limit is 0 |
| `gemini-2.5-flash` | 404 - not available to new users |
| `gemini-flash-latest` | works, but only 20 requests per day |
| **`gemini-flash-lite-latest`** | **working, adequate daily allowance** |

## Resolution

`GEMINI_MODEL` is set to `gemini-flash-lite-latest`. All five educational
features were verified against the running application and confirmed to return
provider-generated output, with `model_used` recorded on each stored response.

`gemini-flash-latest` was used initially and does work, but it resolves to
gemini-3.6-flash, whose free tier allows 20 requests per day. That allowance is
consumed quickly during development and testing, after which every feature
quietly reverts to fallback text. The lite model was selected for a usable
development allowance rather than for output quality.

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
