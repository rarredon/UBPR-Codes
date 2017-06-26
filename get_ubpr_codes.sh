#!/bin/bash

BASEURL=https://cdr.ffiec.gov/Public/
LANDING=DownloadUBPRUserGuide.aspx

echo Getting $LANDING...
wget $BASEURL$LANDING
echo Got $LANDING.

echo Extracting URL for UBPR Complete User Guide...
DOWNLOADURL=$(cat $LANDING | \
		  grep "UBPR Complete User Guide" | \
		  sed -r "s/.*href=\"([^\"]*)*\".*/\1/")
rm $LANDING
echo URL for UBPR Complete User Guide is $DOWNLOADURL.

echo Getting UBPR Complete User Guide...
wget $BASEURL$DOWNLOADURL
echo Got UBPR Complete User Guide.

echo Unzipping UBPR Complete User Guide...
FILE="$(basename $DOWNLOADURL | sed "s/%20/ /g")"
DIR="${FILE%.*}"
unzip "$FILE" -d "$DIR" && rm "$FILE"
echo Unzipped $FILE to $DIR.

echo Combining all PDFs in "$DIR"...
DATE="${DIR##*_}"
PDFOUT="UBPR_Complete_User_Guide_$DATE.pdf"
rm "$DIR/Technical Information.pdf"
pdfunite "$DIR"/* $PDFOUT && rm -rf "$DIR"
echo Combined all PDFs in $DIR into $PDFOUT.

# echo Converting PDF to HTML...
# HTMLOUT=${PDFOUT%.pdf}
# pdftohtml -q $PDFOUT $HTMLOUT && rm $PDFOUT
# echo Converted PDF to HTML.

echo Converting PDF to TXT...
TXTOUT=${PDFOUT%.pdf}.txt
DATEFORMAT="$(date -d $DATE +"%b %d %Y")"
pdftotext $PDFOUT $TXTOUT && rm $PDFOUT
cat $TXTOUT | sed -e "/Page [0-9]\+ of [0-9]\+/d" \
		  -e "/UBPR User's Guide/d" \
		  -e "s/\o14//g" \
		  -e "/^$/d" \
		  -e "/Updated $DATEFORMAT/d" \
		  -r -e "s/([^-]*)--Page ([0-9]+\w*)/SECTION\n\1\n\2/" \
                  -e "s/^Referenced Concepts$/REFERENCE/" > $TXTOUT.sed
mv $TXTOUT.sed $TXTOUT
echo Converted PDF to TXT.

echo Parsing TXT...
OUTFILE=${TXTOUT%.txt}.csv
python parse_ubpr_codes.py $TXTOUT $OUTFILE && rm $TXTOUT
echo Parsed TXT.


