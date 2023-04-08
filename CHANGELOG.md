
## [2.1.1] 2023-04-08
### Fixed
- Defect where a lack of any Qualified Dividends would raise an exception during Dividend Analysis.
- Defect where a sparely populated dividends section would raise an exception when parsing the grand total section.
- Major defect surrounding dividends that are split between qualified and nonqualified. The shares count was totally wrong, and the amount to disqualify could be too high.
- Improve multi-line dividend name parsing (for cases when there is just one dividend for the security).

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