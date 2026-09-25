# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Initial scaffold: config flow (add/options/regenerate token), HTTP view
  serving an iCalendar feed per flow, diagnostic sensor, translations (en/fr).
- Options: a "days behind" window, alongside "days ahead".

### Changed

- Share URLs are now keyed on the token alone (`/api/calendar_share/<token>`)
  instead of the config entry id, which HA does not assign until after the
  flow that would have displayed it finishes.
- Feed window defaults widened to ~13 months behind/ahead (was 1 day behind,
  30 ahead), so a school-year-bound calendar is exposed in full out of the
  box.
