# 🍃 1099 Parser

> Note: Dividend features are in beta. I haven't written tests yet. Use the `--analysis-report` flag to get more details about how decisions are made and double check my work.

## Massive caveat: The parser is no longer compatible with Robinhood or Wealthfront for the 2023 tax year.
Both institutions have simplified their sales reports so that securities sold on a particular day but acquired on different days no have a separate line item for each of the dates acquired (and, in lieu of reporting any acquisition dates at all, the acquired date is simply 'Various'). This breaks the parser (which can be fixed) but more importantly removes a piece of information. Without date acquired, it's no longer possible to analyze (based purely on the consolidated 1099) whether dividends become unqualified.

[![Build](https://github.com/ajwells256/1099-Parser/actions/workflows/build.yaml/badge.svg)](https://github.com/ajwells256/1099-Parser/actions/workflows/build.yaml)

> This project converts standard 1099 tax documents (validated on Robinhood and Wealthfront documents so far) from PDF to CSV file. This tool will be helpful for those who need every transaction in a spreadsheet format for tax reporting purposes. After parsing the tax documents, it will perform some simple analysis on the holding period of securities which reported qualifying dividends.


### Original Work

Copyright (c) 2023 Andrew Wells (ajwells@uchicago.com)

### Original Author

Many kudos to original author Keun Park (kevin.park1217@gmail.com), whose work I used as a foundation upon which to expand.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?business=P3M77TR7L8LBA&item_name=Thanks+for+supporting+my+work%21&currency_code=USD)


## 🚀 Running Locally

### Prerequisites

Make sure you have the following installed on your computer.
- Latest [Python 3](https://www.python.org/downloads/)  
  Must be version 3.6 or higher
- [**Windows Only**] [Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019)  
  In the installer, select
  - C++ build tools
  - the *Windows 10 SDK*
  - the latest version of *MSVC v142 x64/x86 build tools*.


### Installing
```bash
$ python -m pip install wheel
$ python -m pip install --upgrade parse_1099
```
**Note**: If commands above fail, try replacing `python` with `python3`

### Running
```bash
$ parse_1099
usage: parse_1099 [-h] --pdf FILE [--csv FILE] [--silent] [--validate] [--disable-dividend-analysis] [--analysis-report]
```

### Example and Validation

Set the `--validate` flag to print out total values for some columns. Make sure these values match with the PDF!

```bash
$ parse_1099 --pdf consolidated_1099.pdf --validate
Pages: 100%|██████████████████████████████████████████████████████████████| 40/40 [00:03<00:00, 10.41it/s]
>>> Calculated Totals:
    Make sure the values matches with the PDF totals!
    proceeds: $77,521.03, cost: $80,902.05, wash_sales_loss: $3,733.41, gain_loss: $352.39
>>> Saved to output.csv
```

## 🐞 Issues and Bugs
If you have any issues with the tool, please open a GitHub Issue with as much as detail as you can provide.

## Development
### Structure
This is the first python module I've worked on, so the structure may be a little goofy. I tried to structure the project into two parsers, one for 1099-B Proceeds from Broker and Barter Exchange Transactions and one for 1099-DIV Detail for Dividends and Distributions.

In each case, I designed for extensibility via versioning, in case the structure of the data or the presentation of the data on the PDF ever changes. Hypothetically the correct version of the subparser could be detected, but there's no sense writing that functionality until the scenario arises.

### Building
The following will build the python wheel file into the `dist` folder. Note that `python` and `pip` can be exchanged with `python3` and `pip3` depending on your environment configuration.
```bash
$ python -m build
```

The following will update the installed module requiring a version bump.
```bash
$ pip install dist/parse_1099-X.Y.Z-...whl --force-reinstall --no-deps
```