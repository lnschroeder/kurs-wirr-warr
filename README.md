# Fak IV: Modulangebot SS20/KursWirrWarr
This repo contains the code behind the "[Fak IV: Modulangebot SS20 / Kurs WirrWarr](https://docs.google.com/spreadsheets/d/1PUinLo7kEMyUGjpumSx0uliVVIrX3Fa-2kAHdEJIDTA/edit#gid=689835589)" spreadsheet, which was used as an enhanced course catalog for the summer term 2020 at TU Berlin, Faculty 4.

> **Warning** This spreadsheet was only necessary for this one semester and is not maintained any longer.

## Background information
During the first corona-semester at TU Berlin, the official course catalog was not maintained.

**Official alternative:** 
As a replacement, Faculty 4 published a list with over 250 courses, which were offered during the semester (see [WayBackMachine capture](https://web.archive.org/web/20200813121717/https://www.eecs.tu-berlin.de/menue/studium_und_lehre/aktuelles_zum_sose_2020/modulangebot_im_sose_2020)).


**Problems:**
The list was filled manually and contained multiple typos.
Furthermore, this list did not contain any information about the study programs or study areas a course belongs to. This information is necessary for the students and had to be looked up manually in another database (see [MTS](https://moseskonto.tu-berlin.de/moses/modultransfersystem/index.html)).
Thus, it was highly time-consuming to find fitting courses.

**Solution:**
I combined these two data sources in the spreadsheet. This helped the students of Faculty 4 to choose their courses, in no time. It also detected above-mentioned typos, which were reported to the faculty administration.

## Run the code
There is no need for running this. The code will only reproduce the original spreadsheet: [Fak IV: Modulangebot SS20 / Kurs WirrWarr](https://docs.google.com/spreadsheets/d/1PUinLo7kEMyUGjpumSx0uliVVIrX3Fa-2kAHdEJIDTA/edit?usp=sharing).

1. The [jazzpi/mts-scraper](https://github.com/jazzpi/mts-scraper) was used to scrape [MTS](https://moseskonto.tu-berlin.de/moses/modultransfersystem/index.html) for every study program of Faculty 4. See [`mts.sqlite`](mts.sqlite) for the database.
2. [Google Sheets API](https://developers.google.com/sheets/api/) is used to fill the spreadsheet with the MTS data. Thus, you first have to setup a spreadsheet and API access:
   1. Duplicate my Google Spreadsheet [TEMPLATE: Fak IV: Modulangebot SS20 / Kurs WirrWarr](https://docs.google.com/spreadsheets/d/1B6wGsiifzXadgPRE9tDAF5bLFQ7u2D2MZ_BHT_2r3vw/edit?usp=sharing) to a personal spreadsheet (`File` -> `Make a copy`). 
   2. Update `SPREADSHEET_ID` in [`main.py`](main.py) accordingly. 
   3. Create a `credentials.json` as described [here](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id). The result should look  similar to this:
      ```json
      {
        "installed": {
          "client_id": "******************.apps.googleusercontent.com",
          "project_id": "******************",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_secret": "******************",
          "redirect_uris": [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost"
          ]
        }
      }
      ```
3. Run `python3 main.py` and login to your Google account to authorize access to your spreadsheets. This will generate a `token.pickle`.
4. After a minute or two, your spreadsheet will look like this: [Fak IV: Modulangebot SS20 / Kurs WirrWarr](https://docs.google.com/spreadsheets/d/1PUinLo7kEMyUGjpumSx0uliVVIrX3Fa-2kAHdEJIDTA/edit?usp=sharing)
