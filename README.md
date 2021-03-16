# Robinhood 1099 Parser

> This project converts Robinhood Securities 1099 tax document from PDF to CSV file. This tool will be helpful for those who need every transaction in a spreadsheet format for tax reporting purposes.


### Original Work

Copyright (c) 2021 Keun Park (kevin.park1217@gmail.com)

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?business=P3M77TR7L8LBA&item_name=Thanks+for+supporting+my+work%21&currency_code=USD)


## 🚀 Running Locally

Make sure you have Python 3 on your computer. If not, download the latest version from [here](https://www.python.org/downloads/).

Environment Setup  
```bash
git clone https://github.com/kevinpark1217/Robinhood-1099-Parser.git
cd Robinhood-1099-Parser
python -m pip install wheel
python setup.py install
```

Start Parsing!
```bash
➜ rh_1099
usage: rh_1099 [-h] --pdf FILE [--csv FILE] [--silent] [--check]
```

### Example and Checking

Enable `--check` flag to print out total values for some columns. Make sure these values match with the PDF!

```bash
➜ rh_1099 --pdf rh_1099.pdf --check
Pages: 100%|██████████████████████████████████████████████████████████████| 40/40 [00:03<00:00, 10.41it/s]
>>> Calculated Totals:
    Make sure the values matches with the PDF totals!
    proceeds: 77521.03, cost: 80902.05, wash_sales_loss: 3733.41, gain_loss: 352.39
>>> Saved to output.csv
```

## 🐞 Issues and Bugs
If you have any issues with the tool, please open a GitHub Issue with as much as detail as you can provide.