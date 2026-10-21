# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

## [1.0.7] - 2026-10-21

### Changed

- The current share URL is now displayed in the integration's options
  (**Configure**), so it can be retrieved without regenerating the token.

## [1.0.6] - 2026-10-20

### Changed

- README: logo shown at the top (EN and FR).

## [1.0.5] - 2026-10-20

### Changed

- README header: HACS button, release and license badges, title emoji (EN and FR).
- Added brand `logo.png` / `logo@2x.png`; `icon.png` / `icon@2x.png` now use
  the same artwork.

## [1.0.4] - 2026-10-20

### Changed

- README install section now leads with the HACS search; the custom
  repository method is kept as a fallback.

## [1.0.3] - 2026-10-20

### Changed

- README rewritten for a general audience, with a French version
  (`README.fr.md`).

## [1.0.2] - 2026-10-20

### Fixed

- `X-WR-TIMEZONE` now uses the Home Assistant configured time zone instead of
  a hard-coded `Europe/Paris`.
- A percent-encoded non-ASCII token now yields a 403 instead of a 500.
- Events missing `start` or `end` are skipped (debug-logged) instead of
  breaking the whole feed.

## [1.0.1] - 2026-09-25

### Added

- Self-hosted brand icon under `custom_components/calendar_share/brand/`
  (missing from the v1.0.0 release, which predates it).

## [1.0.0] - 2026-09-25

### Added

- Initial scaffold: config flow (add/options/regenerate token), HTTP view
  serving an iCalendar feed per flow, diagnostic sensor, translations (en/fr).
- Options: a "days behind" window, alongside "days ahead".
- Options: a "Full calendar" toggle that shares the whole calendar entity
  (past and future, ~100 years either way), overriding the day counts.

### Changed

- Share URLs are now keyed on the token alone (`/api/calendar_share/<token>`)
  instead of the config entry id, which HA does not assign until after the
  flow that would have displayed it finishes.
- Feed window defaults widened to ~13 months behind/ahead (was 1 day behind,
  30 ahead), so a school-year-bound calendar is exposed in full out of the
  box.
