# Plagiarism-Checker

Plagiarism-Checker checks if segment of your input text can be found on Internet. In short, it checks for plagiarism.
This is a fork based on [this project](https://github.com/architshukla/Plagiarism-Checker), but stripped down, ported to Python 3 and updated to make it work again with Google search engine (and, as a bonus, with Bing).

## How it works

*   It splits the input text in segments
*   It searches the segments online on Google Scholar thanks to [scholarly](https://github.com/scholarly-python-package/scholarly) Python module or on Microsoft Bing.
*   The result page is used to determine similarity with given text query.
*   Similarities result of all request are stored in output text file.

## Required Libraries

*   [scholarly](https://github.com/scholarly-python-package/scholarly)
*   FreeProxy
*   Beautiful Soup 4

You can fetch these using the following command:
```bash
pip3 install scholarly free-proxy beautifulsoup4
```

## Usage

```bash
usage: main.py [-h] [--use_proxy] [-s SEG_START] [-l LIMIT] [-b] [-n SEGMENT_SIZE] text report

Scan a text document for plagiarism.

positional arguments:
  text                  Text file to scan
  report                Text file where the report is written

options:
  -h, --help            show this help message and exit
  --use_proxy           Use an automatically found proxy
  -s SEG_START, --start SEG_START
                        Start the scan from a specific segment (allows to resume a scan)
  -l LIMIT, --limit LIMIT
                        Limits the number of segments scanned (by default there is no limit)
  -b, --bing            Use Bing as search engine (default is Google Scholar)
  -n SEGMENT_SIZE       Size of the segments to use when splitting the input text (default is 9)
```

## Notes

Before starting a scan, you should remove some unwanted text from the input file: lone numbers (from title, legends or references), titles...

You can always stop the pending check (with Ctrl+C). It will write the results found until now. Then you can start from where you have stopped using the `-s` option. The scan is highly likely to hangs when using Google Scholar after an amount of request. Hence the proxy feature and the `-s` option.

Google Scholar gives always a similarity of 1, since the search is done using perfect match.

Microsoft Bing is not specialized in scholar results so you will have to look at the source from which one the result has been found.

