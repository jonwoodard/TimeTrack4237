# TimeTrack4237

This is the student time-tracking software for FRC Team 4237.

##The files directory
This application requires a directory called `files` in the main directory to house the following files:
* timetrack.db  -- the sqlite3 database
* timetrack*.json -- the google credentials for the Google Sheet
* student.csv -- used to import your list of students when the app first runs
* activity.csv -- (optional) used for testing purposes

####Note
The `files` directory will house the database file, the credentials for the google service account,
and it may also house the csv file with student names and barcodes.

* The `student.csv` file must contain records using the format: `barcode,first_name,last_name`
* The `activity.csv` file must contain records using the format: `barcode,checkin,checkout` where both checkin and checkout use the format: `YYYY-MM-DD HH:MM:SS`

This application also requires a `config.json` file in the main directory with the following:

```
{
    "database config":
    {
        "filename": "files/timetrack.db"
    },    
    
    "google config":
    {
        "service account": "files/timetrack*.json",
        "spreadsheet url": "https://docs.google.com/spreadsheets/d/*",
        "worksheet name": "the_name_of_the_worksheet_tab"
    }
}
```

####Note
* The `google config` name-value pair is not required if you do not plan to upload the data to a Google Sheet.
* Replace `timetrack*.json` with the appropriate name. The name will begin with the same name as the Google Sheet and contain a random set of characters after that.
* Replace `https://docs.google.com/spreadsheets/d/*` with the url to the Google Sheet.
* Replace `the_name_of_the_worksheet_tab` with the actual name of the worksheet tab in Google Sheets.


If the database file does not exist, then the application will ask if you want to create the database file
along with the associated tables, indexes, and triggers. It will also ask if you want to import students
using a csv file at that time. You cannot import the csv file later, so have it ready. If you need to import
students after that, then you will need to delete the database file (*.db).
