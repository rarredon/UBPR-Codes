# UBPR-Codes
Program to parse UBPR concept codes from PDF files [published by the FFIEC](https://cdr.ffiec.gov/Public/DownloadUBPRUserGuide.aspx).

To run:

```
>>> ./get_ubpr_codes
```

Requires Python 3 and general scripting utilities (wget, sed, grep, date, pdfunite, pdftotext, unzip).

Script will produce files `UBPR_Complete_User_Guide_DATE.csv` and `UBPR_Complete_User_Guide_DATE_reference.csv` where `DATE` is the date on which the UBPR codes were last updated. The latter describes the codes referenced per section in the former.
