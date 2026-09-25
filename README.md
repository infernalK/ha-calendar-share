# Calendar Share

Custom [Home Assistant](https://www.home-assistant.io/) integration that exposes a chosen calendar entity as an **unauthenticated iCalendar (.ics) subscription feed**, so it can be added natively in the iOS/Android/Google Calendar/Outlook "subscribe to calendar" flow — something Home Assistant's built-in REST API cannot do, since it requires a `Authorization: Bearer` header that mobile calendar apps cannot send.

Security is provided by a long, server-generated, per-flow **token in the URL** instead — validated in constant time, never logged, and independent of your Home Assistant Long-Lived Access Tokens.

> **This integration is only safe to use behind HTTPS.** The token lives in the URL; over plain HTTP it can be read by anything on the network path (proxies, Wi-Fi eavesdroppers, browser history, server logs upstream of Home Assistant). If your Home Assistant instance is not reachable over HTTPS (e.g. via Nabu Casa Cloud or your own reverse proxy with a valid certificate), do not use this integration for anything you would not want read by a third party.

## What it does

- Pick one calendar entity (e.g. `calendar.skolengo_child1`) → get one unguessable URL:
  `https://<your-ha>/api/calendar_share/<token>`
- Add multiple independent flows (one per child, per calendar) — each with its own token, each revocable/regeneratable on its own.
- Read-only: the endpoint only ever calls `calendar.get_events` internally. It cannot create, edit, or delete anything.
- A diagnostic sensor per flow shows the last time the feed was fetched and how many events it currently exposes.

## Installation (HACS)

1. HACS → Integrations → ⋮ → Custom repositories → add this repository URL, category "Integration".
2. Install "Calendar Share", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → "Calendar Share".
4. Choose the calendar to expose. The share URL is shown **once** — copy it immediately.
5. On your phone: Settings → Calendar → Add Account → Add Subscribed Calendar → paste the URL.

## Options (per flow)

- **Days ahead**: sliding window of upcoming days included in the feed (default 30).
- **Regenerate token**: invalidates the current URL immediately and shows the new one once. Update your calendar subscription afterward.

## Security notes

- Tokens are generated with `secrets.token_urlsafe(32)` — never user-chosen.
- Token comparison uses `secrets.compare_digest` (constant-time).
- Tokens are never written to Home Assistant logs, at any log level.
- Each flow is scoped to exactly one calendar entity, chosen explicitly — there is no "all calendars" mode.
- Regenerating or removing a flow takes effect immediately and does not affect other flows.

## Development

```bash
pip install -r requirements_test.txt
ruff check .
mypy --strict custom_components/calendar_share
pytest
```

## License

MIT — see [LICENSE](LICENSE).
