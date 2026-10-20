# Calendar Share

**English** · [Français](README.fr.md)

**Share any Home Assistant calendar with your phone, your family or your colleagues, using a simple link.**

Calendar Share turns a calendar from Home Assistant (school, work, garbage collection, sports club, a Google or CalDAV calendar you already added…) into a private web link. Paste that link into Apple Calendar, Google Calendar, Outlook or any app that can "subscribe to a calendar", and the events appear there and stay up to date by themselves.

## Why use it?

Home Assistant can already show your calendars, but other apps cannot read them: its API requires a login header that calendar apps are unable to send. Calendar Share fixes that by giving each calendar its own **long secret link** (a "token" in the URL) instead of a login. Anyone who has the link can read that one calendar, and nobody else can.

## What you get

- **One link per calendar.** `https://<your-home-assistant>/api/calendar_share/<secret>`
- **As many links as you want**, each independent: one per child, per calendar, per person… Each can be regenerated or removed without touching the others.
- **Read-only.** The link can only display events. It can never create, edit or delete anything.
- **A status sensor** for each link, showing when it was last used and how many events it shares.
- **Choose what is shared**: the whole calendar, or only a window of time (e.g. the last month and the next three).

## ⚠️ Important: use HTTPS

The secret lives inside the link. Over plain HTTP, anyone on the network path could read it. Only use this integration if your Home Assistant is reachable over **HTTPS** (Nabu Casa Cloud, or your own reverse proxy with a valid certificate).

Treat the link like a password: whoever has it can see the calendar. If it leaks, regenerate it (see below).

## Installation

### With HACS (recommended)

1. In HACS, open the ⋮ menu → **Custom repositories**, add this repository's URL with the category **Integration**.
2. Install **Calendar Share** and restart Home Assistant.

### Manually

Copy the `custom_components/calendar_share` folder into the `custom_components` folder of your Home Assistant configuration, then restart.

## Setup

1. Go to **Settings → Devices & Services → Add Integration** and choose **Calendar Share**.
2. Pick the calendar you want to share.
3. Your link is displayed **once**. Copy it right away.
4. Subscribe to it in your calendar app:
   - **iPhone / iPad:** Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.
   - **Google Calendar (on a computer):** Other calendars (+) → From URL. It then also shows on your Android phone.
   - **Outlook:** Add calendar → Subscribe from web.
   - **Any other app:** look for "subscribe to a calendar" or "add calendar from URL".

Calendar apps refresh subscribed calendars on their own schedule (from a few minutes to several hours), so new events may take a while to appear.

## Options

You can change these at any time from the integration's **Configure** button.

| Option | What it does |
| --- | --- |
| **Full calendar** | Shares everything the calendar contains, past and future. The two settings below are then ignored. |
| **Days ahead** | How far into the future events are shared (default: 400 days, max 10 years). |
| **Days behind** | How far into the past events are shared (default: 400 days, max 10 years). |
| **Regenerate token** | Creates a new link and instantly disables the old one. The new link is shown once; update your subscriptions afterwards. |

The default window (about 13 months each way) is wide enough for most calendars, including school-year ones, so you rarely need to change anything.

## Security

- Links are generated automatically with `secrets.token_urlsafe(32)`. You cannot choose a weak one.
- The secret is checked in constant time and is never written to Home Assistant's logs.
- Each link is tied to exactly one calendar that you picked. There is no "share everything" link.
- Regenerating or removing a link takes effect immediately and does not affect the others.
- The link is separate from your Home Assistant accounts and Long-Lived Access Tokens.

## Troubleshooting

- **The app says the link is invalid / 403:** the link was regenerated or mistyped. Copy the current one again.
- **Events are missing:** check the options (days behind / ahead, or turn on *Full calendar*), then wait for your app to refresh.
- **Wrong hours:** the feed uses the time zone set in Home Assistant (Settings → System → General).

## Development

```bash
pip install -r requirements_test.txt
ruff check .
mypy --strict custom_components/calendar_share
pytest
```

## License

MIT, see [LICENSE](LICENSE).
