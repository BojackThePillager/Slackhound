# Changelog

## Released - 8-11-2025

### Added
- Support for dual tokens: User token (loaded from `token.txt` or `--token1` CLI argument) and Bot token (loaded from `SLACK_TOKEN_BOT` environment variable or `--token2` CLI argument).
- Centralized `api_request()` function that automatically selects the appropriate token based on the API endpoint.
- Automatic retry logic in `api_request()` to handle `not_allowed_token_type` errors by switching tokens.
- Color-coded console output using the `Colors` module for better readability.
- Argument parsing upgraded to `argparse` for improved usability and clarity.
- Ability to override tokens via command line arguments (`--token1`, `--token2`).
- Pretty-printing JSON responses using YAML formatting for easier inspection.
- Added helpful error messages and validation for required arguments in CLI options.
- Functions refactored to use the unified `api_request()` interface, reducing redundant code.

### Changed
- Migrated from deprecated `optparse` to modern `argparse`.
- Removed duplicate token reading logic; tokens are loaded once and managed centrally.
- All Slack API interactions now go through a single request function with standardized error handling.
- File uploads now check file existence before attempting upload.
- CSV exports and SQLite database saving improved for reliability and cleaned columns.
- Switched API request methods appropriately (`GET` vs `POST`) and ensured consistent parameter passing.
- Adjusted CLI option handling to require necessary arguments upfront, preventing incomplete calls.

### Fixed
- Fixed errors caused by bot tokens being used on endpoints that require user tokens (and vice versa) by implementing token selection and retries.
- Resolved issues with uploading files and sending reminders where token permission mismatches caused failures.
- Improved error handling and messaging across all API calls for clearer troubleshooting.

