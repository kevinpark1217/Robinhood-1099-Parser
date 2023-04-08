
## [2.1.0] 2023-04-08
### Changed
- Added short-hand flags for the existing command line parameters.

## [2.0.0] 2023-04-07
### Added
- Added search functionality for ex dividend dates.
- Added parsing of dividends.
- Added analysis of dividends and sales to determine whether qualified dividends need to be considered nonqualified.

### Changed
- Downgraded python version requirement to `>= 3.6` for ease of use on ubuntu.
- Renamed tool to `parse_1099` to reflect that it's not specific to Robinhood.

## [1.0.1]
- Updated README.md to utilize `pip install rh_1099`
- Updated setup.py to bump Python version requirement to `>= 3.8`

## [1.0.0]
- Initial release