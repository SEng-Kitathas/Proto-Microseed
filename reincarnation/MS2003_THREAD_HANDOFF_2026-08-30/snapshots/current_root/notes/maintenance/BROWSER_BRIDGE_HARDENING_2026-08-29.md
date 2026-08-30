# Browser Bridge Hardening — 2026-08-29

## Scope / authority
Infrastructure maintenance only. No Microseed organism code mutation. No novelty/promotion authority.

User explicitly authorized launching the browser bridge/server and using online models. The online-review attempt preserved separate access/consent boundaries: no CAPTCHA bypass, no credential automation, and no acceptance of a site's explicit public-sharing/legal terms on the user's behalf.

## Initial bridge state
Server-native browser tools were present but `browser.health` initially failed because no service listened on `127.0.0.1:4471`.

Stale audit launcher:
`E:\new pc\AI_Pushes_Sandbox\projects\browser_bridge_audit\START_BROWSER_BRIDGE.cmd`
pointed to nonexistent:
`C:\Users\ancal\Desktop\pcmmad_receiver\browser_bridge_service.py`.

Actual current baseline implementation:
`C:\Users\ancal\Desktop\PCMMAD_receiver\baseline\pcmmad_receiver\browser_bridge_service.py`

Pre-hardening SHA-256:
`ca312ec5a396d416d475f0e17b3dabaa7324c762e3a003725a95f87e5ff14b85`.

An RC1 package copy with that original SHA was intentionally left untouched and remains a recovery/reference surface.

## Dependency repair
The baseline receiver `.venv` contained Flask but not Playwright even though the README required it and `requirements.txt` did not declare it.

Installed Playwright 1.62.0 only into the receiver isolated venv:
job `job-e88d4ff02e28`, exit 0.

Chrome/Edge smoke tests through Playwright succeeded without downloading a bundled browser:
- Chrome 151.0.7922.174;
- Edge 151.0.4129.107.

`requirements.txt` now includes `playwright==1.62.0`.

## Online-review route findings before hardening
A dedicated isolated browser profile/session was used; ordinary user browser state/credentials were not attached.

Observed route classes:
- Duck.ai: anonymous model selection and Web Search worked, then human CAPTCHA appeared; not bypassed.
- Perplexity, Mistral Le Chat, Pi: Cloudflare/bot verification; not bypassed.
- Microsoft Copilot: region unavailable.
- DeepSeek: CloudFront 403.
- Grok/Qwen Studio: messaging would create/accept terms/privacy use; no project prompt submitted through an unreviewed acceptance flow.
- Arena Direct/Search: named external models including `claude-sonnet-4-6-search` were available, but first-use agreement explicitly stated conversations may be disclosed to providers/publicly and used for automated evaluation. The agreement was not accepted on the user's behalf.
- HuggingChat: anonymous landing/direct model route exposed named `zai-org/GLM-5.3-Flash` and enabled `Web Search (Exa)` MCP, but starting actual chat redirected to Hugging Face OAuth; headless login path was CloudFront-blocked.

No external hosted-model review was admitted from these attempts.

## Bridge failure localization
The original Flask bridge intentionally used `threaded=False` with Playwright's synchronous API, but route operations inherited Playwright's ~30-second default action timeout.

Observed effect:
- reactive-site `page.click` / `page.fill` calls could block the single bridge lane for tens of seconds;
- health/readback calls queued behind the blocking route;
- bridge job `job-778becc3b07f` later exited after ~741 s following multiple slow/502 click paths.

The single-threaded architecture itself was retained because sync Playwright is thread-affine. The repair instead bounds route latency.

## Hardening embodied
Baseline bridge only; RC1 copy untouched.

### `browser_bridge_service.py`
Post-hardening SHA-256:
`56877576b622b59f4a2ef432a60aee8b39792100b3381757ac16f167d994f20a`.

Added environment-configurable defaults:
- action timeout 8000 ms;
- navigation timeout 25000 ms;
- maximum route timeout override 60000 ms.

`/health` now reports all three limits.

Bounded `timeout_ms` handling added to:
- `/navigate`;
- `/fill`;
- `/click`;
- `/press`;
- `/text`;
- startup/new-page navigations where applicable.

New `/input` route:
- waits for visible element under bounded timeout;
- uses native input/textarea value setter or contenteditable text;
- dispatches bubbling input/change events;
- returns value length for immediate readback.

Existing page objects now receive page-level default action/navigation timeouts when selected/created.

Flask remains `threaded=False` by design.

### requirements
`requirements.txt` post SHA:
`8e9392cfcc7a9db70056663c0e5b241dc8783ab88bea55d485ed1a33136198a5`.

### package launcher
`START_BROWSER_BRIDGE.cmd` now resolves and uses the package `.venv` explicitly.
Post SHA:
`235cf0ba08af706297f5dd98e9ce9943ba5feca3d23d128b6fa91104862cd8e6`.

### audit launcher
Stale external audit launcher updated to the actual baseline receiver/venv path.
Post SHA:
`656c842f06c14b04c2d502e2958d539cc2a831bcca6d8cecac3f7f92b7b73f91`.

### README
Operational timeout/input documentation appended.
Post SHA:
`be10b12ff56fe26eef76928b51ff1c2e6348ff797a31444807752419e10bb344`.

## Verification
Patched service compiled successfully with receiver venv.

Hardened service durable job:
`job-a918b9311c9f`.

Health readback after start:
- `action_timeout_ms=8000`;
- `navigation_timeout_ms=25000`;
- `max_route_timeout_ms=60000`;
- Playwright true;
- zero initial sessions.

Bounded smoke suite used a fresh headless Chrome data-URL page.
Verified:
1. `/text` returned `ready`.
2. `/input` set textarea to `event-path-ok` and readback matched exactly.
3. `/click` changed output to `clicked`.
4. deliberate missing selector with `timeout_ms=1000` returned `CLICK_FAILED` 502 in **1.031 s**.
5. immediate `/health` answered 200 in **0.016 s** after that route timeout.
6. smoke session closed cleanly with no close errors.

This directly verifies that a slow/missing selector no longer monopolizes the bridge for the former default timeout interval.

## Current browser-review posture
The infrastructure is now materially healthier and ready for future online-model work.

However current public/anonymous hosted-model routes remain blocked by one of:
- human CAPTCHA/security challenge;
- account/OAuth requirement;
- region availability;
- explicit legal/public-sharing consent not accepted on user's behalf.

Do not describe this as absence of online-model capability. It is an **access/consent boundary** after infrastructure readiness.

## Reopen conditions
Reopen online hosted-model review when:
- user explicitly authorizes a specific site's consent/public-sharing terms; or
- a clean authenticated/API model route is configured; or
- another public endpoint becomes available without CAPTCHA/login/new consent.

No external-review result has been admitted from the browser lane yet.
