# Plagiarism-Checker

A utility to check if a document's contents are plagiarised.
This is a fork based on [this project](https://github.com/architshukla/Plagiarism-Checker), but stripped down, ported to Python 3 and updated to make it work again with Google.

## How it works

*   It splits the input text in segments
*   It searches the segments online on Google Scholar thanks to [scholarly](https://github.com/scholarly-python-package/scholarly) Python module or on Microsoft Bing.
*   The result page is used to determine similarity with given text query.
*   Similarities result of all request are stored in output text file.

## Required Libraries

*   [scholarly](https://github.com/scholarly-python-package/scholarly)
*   FreeProxy
*   Beautiful Soup 4


### GETTING LIBRARIES ON LINUX

* Install dependent libraries

```bash
sudo pip3 install scholarly free-proxy beautifulsoup4
```

### GETTING LIBRARIES ON WINDOWS

These steps assume you already have python (with pip) installed and that python is in your windows environment variables.

```bash
sudo pip3 install scholarly free-proxy beautifulsoup4
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

Before starting a check, you should remove some unwanted text from the input file: lone numbers (from title, images or references), titles...

You can always stop the pending check (with Ctrl+C). It will write the results found until now. Then you can start from where you have stopped using the `-s` option. Please note that Google is strict upon using its search engine. The scan is highly likely to hangs after an amount of request. Hence the proxy feature and `-s` option.

Google Scholar gives always a similarity of 1, since the search are done using perfect match.

Microsoft Bing is not speciliazed in scholar results so you will have to look at the source from which one the result has been found.

