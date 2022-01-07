# TimeTrack4237

This is the student time-tracking software for FRC Team 4237.

The application requires a "config.json" file in the main directory with the following:

```
{
    "database config":
    {
        "filename": "files/*.db"
    },    
    
    "google config":
    {
        "service account": "files/*.json",
        "spreadsheet url": "https://docs.google.com/spreadsheets/d/*",
        "worksheet name": "enter the tab name"
    }
}
```

The "google config" name-value pair is not required if you do not plan to upload the data to a Google Sheet.

The files directory will house the database file (*.db), the credentials for the google service account,
and it may also house the csv file with student names and barcodes. The csv file must contain records using
the format barcode,first_name,last_name.

If the database file does not exist, then the application will ask if you want to create the database file
along with the associated tables, indexes, and triggers. It will also ask if you want to import students
using a csv file at that time. You cannot import the csv file later, so have it ready. If you need to import
students after later, then you will need to delete the database file (*.db).