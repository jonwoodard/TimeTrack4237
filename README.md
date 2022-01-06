# TimeTrack4237

This is the student time-tracking software for FRC Team 4237.

The program requires a "config.json" file in the main directory with the following format:

```
{
    "database config":
    {
        "filename": "files/*.db"
    },    
    
    "google config":
    {
        "service account": "credentials/*.json",
        "spreadsheet url": "https://docs.google.com/spreadsheets/d/*",
        "worksheet name": "enter the tab name"
    }
}
```

The "google config" name-value pair is not required if you do not plan to upload the data to a Google Sheet.
