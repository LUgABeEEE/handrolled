# Changelog

## [0.1.1] — 2026-10-31

### Added

- `DSH_KB_DEEP_KEY_NAME` names the key to read out of the credentials file
  (default `DEEP_API_KEY`).  A host that already keeps its key under another
  name — a shared credentials file for several services — no longer has to copy
  the secret into a second file just to be readable.  The vendor name stays out
  of the code either way.

