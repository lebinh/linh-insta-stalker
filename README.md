# linh-insta-stalker
Script to update Google Spreadsheet doc that can be used as a tracking database
for Instagrammers.


## Usage

Modify the constants at the top of stalker.py as needed and then:

```
python stalker.py
```

## Credentials

You don't need any Instagram credential as this uses a public (but undocumented)
JSON API for Instagram user info. But you will need to get a client secret file for
Google Spreadsheet API.  [This post from Twilio](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
has a guide on how-to obtain one. Be noted that tracking document need to be shared
with that service account before you can update the doc with this script.
