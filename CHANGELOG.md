# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

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
