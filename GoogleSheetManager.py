import os
import gspread
import gspread.utils
import json

from datetime import datetime, timedelta
from DatabaseManager import DatabaseManager

# The CONFIG_FILENAME is also defined in TimeTrack4237.py
CONFIG_FILENAME = 'config.json'
THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class GoogleSheetManager:
    """This class is only used in the DatabaseManager.upload_student_data_to_google_sheet() method.
    When the object is created, it automatically uploads the data to the google sheet."""

    # IMPORTANT: gspread uses the Google Sheets API v4, which introduced Usage Limits
    #   • 300 write requests per minute,
    #   • 60 write requests per minute per user, and
    #   • unlimited write requests per day.
    # When the application hits that limit, you get an APIError 429 RESOURCE_EXHAUSTED.
    # These are the same limits for reading, but that is not an issue with this application.
    # Use the update() and batch_update() methods to help reduce API calls.

    def __init__(self, db_manager_or_filename):
        if isinstance(db_manager_or_filename, DatabaseManager):
            self.__db_manager = db_manager_or_filename
        else:  # elif isinstance(db_manager_or_filename, str):
            self.__db_manager = DatabaseManager(db_manager_or_filename)

        # self.__student_names_and_barcode_list = [ (lastname0, firstname0, barcode0), ... ]
        self.__student_names_and_barcode_list = []

        # self.__student_hours_list = [ (lastname0, firstname0, barcode0, year1, week1, week1_hours),
        #                               (lastname0, firstname0, barcode0, year2, week2, week2_hours), ...]
        # Note: there is one tuple for each week that a student has logged hours,
        #   so each student will have several tuples with each tuple indicating weekly hours.
        self.__student_hours_list = []

        # self.__header_list[0] = ['', '', '', '', year1, year1, year1, ...,  year1,  year2, ... ]
        # self.__header_list[1] = ['', '', '', '', week1, week2, week3, ..., week51, week52, ... ]
        # self.__header_list[2] = ['Last name', 'First name', 'Barcode', 'Hours', sunday1, sunday2, sunday3, ... ]
        self.__header_list = []

        # self.__data_list = [ ['lastname', 'firstname', 'barcode', total_hours, week1_hours, week2_hours, ...] ...]
        self.__data_list = []

    def upload_data(self) -> tuple:
        success = False
        message = ''

        success, message, self.__student_names_and_barcode_list, self.__student_hours_list = self.__db_manager.get_google_sheet_data()
        # If there are no names and barcodes, then there is nothing to upload.
        # The student_hours_list could be empty, before any student has logged hours, which is fine.
        if not (success and self.__student_names_and_barcode_list):
            self.__clean_up()
            return False, 'Database Error', message

        self.__create_header_list()
        # The header list must have 3 lists at this point. [ [years...], [weeks...], [dates...] ]
        if len(self.__header_list) != 3:
            self.__clean_up()
            return False, 'Header List Error', 'The header list failed to create properly.'

        self.__create_data_list()
        # The data_list should NOT be empty at this point.
        if not self.__data_list:
            self.__clean_up()
            return False, 'Data List Error', 'The data list failed to create properly.'

        success, message, google_config = self.__get_google_config()
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        success, message, wb, ws = self.__open_sheet(google_config)
        if not (success and wb and ws):
            self.__clean_up()
            return False, 'Google Sheets Error', message

        success, message = self.__remove_data_and_formatting(wb, ws)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        num_rows = len(self.__data_list) + 1
        num_cols = len(self.__header_list[2])  # checked above that header_list has 3 elements

        # The order below matters: (1) resize the sheet, (2) format the sheet, (3) enter the data
        # The barcode column must be set to TEXT number format before the data is entered,
        #   otherwise any leading zeros will be lost.
        success, message = self.__resize_sheet(ws, num_rows, num_cols)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        success, message = self.__format_sheet(wb, ws)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        success, message = self.__enter_data_on_sheet(ws)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        self.__clean_up()
        return True, 'Upload Successful', 'The data was uploaded successfully to the Google Sheet.'

    def __create_header_list(self) -> None:
        """
        This *private* method creates the header_list which contains 3 sub-lists.
        The first two lists are needed to create the data_list later and the last list is the Google Sheet header.
        header_list[0] = ['', '', '', '', year1, year1, year1, ...,  year1,  year2, ... ]
        header_list[1] = ['', '', '', '', week1, week2, week3, ..., week51, week52, ... ]
        header_list[2] = ['Last name', 'First name', 'Barcode', 'Hours', sunday1, sunday2, sunday3, ... ]

        **Note**: year1, week1, and sunday1 in the 3 lists correspond to the sunday in that week and year.

        :return: None
        """

        self.__header_list = [['', '', '', ''], ['', '', '', ''], ['Last Name', 'First Name', 'Barcode', 'Hours']]

        if self.__student_hours_list:
            # This is a sweet way to find the earliest week and latest week with data in the student_hours_list.
            first = min(self.__student_hours_list, key=lambda x: int(x[3]) + int(x[4]) / 54)
            last = max(self.__student_hours_list, key=lambda x: int(x[3]) + int(x[4]) / 54)

            # Get the starting week/year and ending week/year
            start_year = int(first[3])
            start_week = int(first[4])
            end_year = int(last[3])
            end_week = int(last[4])

            # Get the day number of the first sunday of the year
            start_sunday = (7 - int(datetime(start_year, 1, 1).strftime('%w'))) % 7
            end_sunday = (7 - int(datetime(end_year, 1, 1).strftime('%w'))) % 7

            # Get the date of the first sunday of the year
            start_date = datetime(start_year, 1, 1 + start_sunday)
            end_date = datetime(end_year, 1, 1 + end_sunday)

            # Get the sunday of the starting week/year and ending week/year
            start_date += timedelta(days=(start_week - 1) * 7)
            end_date += timedelta(days=(end_week - 1) * 7)

            self.__header_list = [['', '', '', ''], ['', '', '', ''], ['Last Name', 'First Name', 'Barcode', 'Hours']]

            # Create the rest of the header_list, adding an element to each sub-list for the corresponding
            # year, week, and sunday date in range from start_date to end_date
            while start_date.date() <= end_date.date():
                self.__header_list[0] += [start_date.strftime('%Y')]
                self.__header_list[1] += [start_date.strftime('%U')]
                self.__header_list[2] += [start_date.strftime('%m/%d/%Y')]
                start_date += timedelta(days=7)

    def __create_data_list(self) -> None:
        """
        This *private* method creates the data_list which contains multiple lists, one for each student.
        data_list[0] = ['lastname0', 'firstname0', 'barcode0', 'total_hours0', 'week1_hours', 'week2_hours', ... ]

        :return: None
        """

        # Convert the "student_names_and_barcode_list" into a list of lists along with a spot for the total hours
        # This method will be adding elements to each of these sub-lists, which cannot be done with tuples.
        # "data_list" will be a list of lists: [ [lastname, firstname, barcode, 0.0], ... ]
        for record in self.__student_names_and_barcode_list:
            self.__data_list.append(list(record + (0.0,)))

        data_list_index = 0
        header_list_index = 4

        for record in self.__student_hours_list:
            # record = ('lastname', 'firstname', 'barcode', 'year', 'week number', 'week hours')

            # Find the student that this "record" belongs to in the "data_list"
            # Note: some students may not have any hours yet and must be skipped over
            while data_list_index < len(self.__data_list) and record[2] != self.__data_list[data_list_index][2]:
                data_list_index += 1
                header_list_index = 4

            year = int(record[3])
            week_num = int(record[4])
            week_hours = record[5]
            self.__data_list[data_list_index][3] += week_hours

            # If the week number is 0, then the Sunday at the beginning of that week was in the previous year
            if week_num == 0:
                year -= 1
                week_num = int(datetime(year, 12, 31).strftime('%W'))  # either 52 or 53

                # Check if the last week of the previous year data
                same_year = (str(year) == str(self.__header_list[0][header_list_index-1]))
                same_week = (str(week_num) == str(self.__header_list[1][header_list_index-1]))

                if same_year and same_week:
                    week_hours += self.__data_list[data_list_index].pop()
                    header_list_index -= 1

            # Append the weekly hours onto the "data_list" for each student
            # data_list = [ ['lastname', 'firstname', 'barcode', total_hours, week1_hours, week2_hours, ...] ...]
            # Find the correct column for this "record" in the "data_list"
            # If a student only worked week 1 and week 3, then a blank needs to be added for week 2.
            done = False
            while not done:
                header_year = int(self.__header_list[0][header_list_index])
                header_week_num = int(self.__header_list[1][header_list_index])

                if year == header_year and week_num == header_week_num:
                    # Stop the loop if this is the correct column
                    done = True
                else:
                    # Add a blank if this is not the correct column
                    self.__data_list[data_list_index] += ['']

                header_list_index += 1

            # Add this "record" to the "data_list"
            self.__data_list[data_list_index].append(week_hours)

    def __get_google_config(self) -> tuple:
        """
        This *private* method gets the configuration data in order to open the Google Sheet.

        :return: success, message, config info
        """

        config_file = os.path.join(THIS_DIRECTORY, CONFIG_FILENAME)

        # Check if the google config file exists.
        if not os.path.isfile(config_file):
            return False, 'Google config file does not exist.', {}

        # Open the files if it exists.
        with open(config_file, 'r') as fh:
            try:
                # Read the json string from the file into the config dictionary.
                config = json.load(fh)
                # Store the google config dictionary
                google_config = config['google config']
                return True, '', google_config
            except Exception as e:
                return False, 'Google config file is unreadable.', {}

    def __open_sheet(self, google_config: dict) -> tuple:
        """
        This *private* method opens the Google Sheet.

        :param google_config: the google config dictionary to open the Google Sheet
        :return: wb = Google Spreadsheet file, ws = one Worksheet in the file
        """
        try:
            # See the gspread documentation to open a Google Sheet
            folder, file = os.path.split(google_config['service account'])
            credential_file = os.path.join(THIS_DIRECTORY, folder, file)

            gc = gspread.service_account(credential_file)
            wb = gc.open_by_url(google_config['spreadsheet url'])
            ws = wb.worksheet(google_config['worksheet name'])
            return True, '', wb, ws
        except Exception as e:
            return False, 'There was an error with the Google Sheets file.', None, None

    def __remove_data_and_formatting(self, wb: gspread.Spreadsheet, ws: gspread.Worksheet) -> tuple:
        """
        This *private* method removes all data and formatting from the sheet.
        Without this, when new rows and columns are added, the format from the existing cells is used.

        :param wb: the Google Spreadsheet file
        :param ws: the one Google Worksheet in the file
        :return: None
        """

        # See the Google Sheets API and gspread documentation for help
        sheet_id = ws._properties['sheetId']
        if sheet_id:

            # Clear all formatting on the sheet
            d0 = {'updateCells': {
                'range': {'sheetId': sheet_id},
                'fields': 'userEnteredFormat'}}
            body = {'requests': [d0]}

            if ws.col_count > 0:
                # Reset the column width to 100 pixels (default) so that new columns are added with this default size.
                d1 = {'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': ws.col_count},
                    'properties': {'pixelSize': 100},
                    'fields': 'pixelSize'}}
                body.get('requests', []).append(d1)

            if ws.row_count > 0:
                # Reset the row height to 21 pixels (default) so that new rows are added with this default size.
                d2 = {'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': ws.row_count},
                    'properties': {'pixelSize': 21},
                    'fields': 'pixelSize'}}
                body.get('requests', []).append(d2)

            d3 = {'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'gridProperties': {'frozenRowCount': 0, 'frozenColumnCount': 0}},
                'fields': 'gridProperties(frozenRowCount, frozenColumnCount)'}}
            body.get('requests', []).append(d3)

            try:
                # Clear all data on the sheet
                # ws.clear() cannot be completed with a ws.batch_update() call, so it is done separate
                response = ws.clear()

                if len(body.get('requests', [])) > 0:
                    wb.batch_update(body)
                return True, ''
            except Exception as e:
                return False, 'There was an error removing the previous data and formatting from the Google Sheet.'

    def __resize_sheet(self, ws: gspread.Worksheet, num_rows: int, num_cols: int) -> tuple:
        """
        This *private* method resizes the worksheet to the given dimensions.

        :param ws: the one Google Worksheet in the file
        :param num_rows: number of rows
        :param num_cols: number of columns
        :return: None
        """
        try:
            if num_rows > 0 and num_cols > 0:
                # ws.resize() calls batch_update
                response = ws.resize(rows=num_rows, cols=num_cols)

                # NOTE: ws.resize() has a known BUG, it does not update the ws.row_count and ws.col_count properties
                #   of the gspread.Worksheet object. Some gspread methods rely on these properties.
                #   So the following two statements update those properties.
                ws._properties['gridProperties']['rowCount'] = num_rows
                ws._properties['gridProperties']['columnCount'] = num_cols
            return True, ''
        except Exception as e:
            return False, 'There was an error resizing the Google Sheet.'

    def __format_sheet(self, wb: gspread.Spreadsheet, ws: gspread.Worksheet) -> tuple:
        """
        This *private* method formats the worksheet.
        :param wb: the Google Spreadsheet file
        :param ws: the one Google Worksheet in the file
        :return: None
        """

        # NOTE: The gspread method ws.format() could also be used to do the first six formats below.
        # However, each call to ws.format() would use a separate batch_update() API call.
        # So this uses the native Google Sheets API approach, but it only requires one batch_update() at the end.
        num_rows = ws.row_count
        num_cols = ws.col_count

        # See the Google Sheets API and gspread documentation for help
        sheet_id = ws._properties['sheetId']
        if sheet_id:
            body = {'requests': []}
            if num_rows > 0 and num_cols > 3:
                # A1:D1 - Set the cell background color and text to bold
                d1 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 0, 'endRowIndex': 1,
                              'startColumnIndex': 0, 'endColumnIndex': 4},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 217 / 255, 'green': 210 / 255, 'blue': 233 / 255},
                            'textFormat': {'bold': True}}},
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'}}
                body.get('requests', []).append(d1)

                # A1:C? - Set the horizontal alignment to LEFT
                d2 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 0, 'endRowIndex': num_rows,
                              'startColumnIndex': 0, 'endColumnIndex': 3},
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {'type': 'TEXT'},
                            'horizontalAlignment': 'LEFT'}},
                    'fields': 'userEnteredFormat(numberFormat,horizontalAlignment)'}}
                body.get('requests', []).append(d2)

                # D1:D? - Set the horizontal alignment to RIGHT
                d3 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 0, 'endRowIndex': num_rows,
                              'startColumnIndex': 3, 'endColumnIndex': 4},
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': 'RIGHT'}},
                    'fields': 'userEnteredFormat(horizontalAlignment)'}}
                body.get('requests', []).append(d3)

            if num_rows > 1 and num_cols > 3:
                # D2:D? - Set number format to NUMBER with 2 decimal places
                d4 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 1, 'endRowIndex': num_rows,
                              'startColumnIndex': 3, 'endColumnIndex': 4},
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {'type': 'NUMBER', 'pattern': '0.00'}}},
                    'fields': 'userEnteredFormat(numberFormat)'}}
                body.get('requests', []).append(d4)

            if num_rows > 0 and num_cols > 4:
                # E1:?1 - Set background color, horizontal alignment, number format, and bold.
                d5 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 0, 'endRowIndex': 1,
                              'startColumnIndex': 4, 'endColumnIndex': num_cols},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 201 / 255, 'green': 218 / 255, 'blue': 248 / 255},
                            'horizontalAlignment': 'CENTER',
                            'numberFormat': {'type': 'DATE', 'pattern': 'm"/"d'},
                            'textFormat': {'bold': True}}},
                    'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,numberFormat,textFormat)'}}
                body.get('requests', []).append(d5)

            if num_rows > 1 and num_cols > 4:
                # E2:?? - Set horizontal alignment to CENTER and number format to NUMBER with 2 decimals.
                d6 = {'repeatCell': {
                    'range': {'sheetId': sheet_id,
                              'startRowIndex': 1, 'endRowIndex': num_rows,
                              'startColumnIndex': 4, 'endColumnIndex': num_cols},
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': 'CENTER',
                            'numberFormat': {'type': 'NUMBER', 'pattern': '0.00'}}},
                    'fields': 'userEnteredFormat(horizontalAlignment,numberFormat)'}}
                body.get('requests', []).append(d6)

            if num_cols > 3:
                # Columns A:D - Set the width to 100 pixels (default)
                d7 = {'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 4},
                    'properties': {'pixelSize': 100},
                    'fields': 'pixelSize'}}
                body.get('requests', []).append(d7)

            if num_cols > 4:
                # Columns E:? - Set the width to 50 pixels
                d8 = {'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 4, 'endIndex': num_cols},
                    'properties': {'pixelSize': 50},
                    'fields': 'pixelSize'}}
                body.get('requests', []).append(d8)

            if num_rows > 0:
                # Rows 1:? - Set the height to 21 pixels (default)
                d9 = {'updateDimensionProperties': {
                    'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': num_rows},
                    'properties': {'pixelSize': 21},
                    'fields': 'pixelSize'}}
                body.get('requests', []).append(d9)

            if num_rows > 1:
                # Row 1 and Columns A:D - Set to frozen
                d10 = {'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'gridProperties': {'frozenRowCount': 1}},
                    'fields': 'gridProperties(frozenRowCount)'}}
                body.get('requests', []).append(d10)

            if num_cols > 4:
                # Row 1 and Columns A:D - Set to frozen
                d11 = {'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'gridProperties': {'frozenColumnCount': 4}},
                    'fields': 'gridProperties(frozenColumnCount)'}}
                body.get('requests', []).append(d11)

            try:
                if len(body.get('requests', [])) > 0:
                    wb.batch_update(body)
                return True, ''
            except Exception as e:
                return False, 'There was an error formatting the Google Sheet.'

    def __enter_data_on_sheet(self, ws: gspread.Worksheet) -> tuple:
        """
        This *private* method enters the data into the worksheet.

        :param ws: the one Google Worksheet in the file
        :return:
        """
        if self.__data_list:
            data = [self.__header_list[2]] + self.__data_list
        else:
            data = [self.__header_list[2]]

        try:
            response = ws.update('A1', data, raw=False)
            return True, ''
        except Exception as e:
            return False, 'There was an error entering the data on the Google Sheet.'

    def __clean_up(self):
        self.__student_names_and_barcode_list.clear()
        self.__student_hours_list.clear()
        self.__header_list.clear()
        self.__data_list.clear()
