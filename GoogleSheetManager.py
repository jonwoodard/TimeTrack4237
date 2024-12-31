import gc
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

        #self.__raw_data_list = [ [ 'lastname', 'firstname', 'barcode', checkin, checkout, hours ] ]
        self.__raw_data_list = []

    def upload_data(self) -> tuple:
        # Garbage collection slows down the process, so disable it during the upload process.
        # Garbage collection is enabled again in the __clean_up() method.
        gc.disable()

        success = False
        title = ''
        message = ''

        success, message, self.__student_names_and_barcode_list, self.__student_hours_list = self.__db_manager.get_google_sheet_data()

        # Get the Google config info
        success, message, google_config = self.__get_google_config()
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        # Open the spreadsheet, but wait to open the worksheet
        success, message, wb = self.__open_spreadsheet(google_config)
        if not (success and wb):
            self.__clean_up()
            return False, 'Google Sheets Error', message

        # Check if the worksheets exist in the spreadsheet
        self.__check_spreadsheet(wb, google_config)

        # Upload the worksheet of formatted and condensed data
        success, title, message = self.__upload_worksheet(google_config, wb)
        if not success:
            self.__clean_up()
            return False, 'Database Error', message

        # Upload the full activity table raw data
        success, title, message = self.__upload_raw_data_worksheet(google_config, wb)
        if not success:
            self.__clean_up()
            return False, 'Database Error', message

        # Clean it up and return a "successful" message
        self.__clean_up()

        return True, 'Upload Successful', 'The data was uploaded successfully to the Google Sheet.'

    def __upload_worksheet(self, google_config: dict, wb: gspread.Spreadsheet) -> tuple:

        success = False
        message = ''

        ws_name = google_config.get('worksheet name')
        if not ws_name:
            return False, 'Google Sheets Error', 'The "worksheet name" key is missing in config.json file.'

        success, message, ws = self.__open_sheet(wb, ws_name)
        if not (success and ws):
            self.__clean_up()
            return False, 'Google Sheets Error', message

        self.__create_header_list()
        # The header list must have 3 lists at this point. [ [years...], [weeks...], [dates...] ]
        if len(self.__header_list) != 3:
            self.__clean_up()
            return False, 'Header List Error', 'The header list failed to create properly.'

        self.__create_data_list()

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

        if self.__data_list:
            data = [self.__header_list[2]] + self.__data_list
        else:
            data = [self.__header_list[2]]

        success, message = self.__enter_data_on_sheet(ws, data)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        return True, 'Upload Successful', 'The worksheet was uploaded successfully to the Google Sheet.'

    def __upload_raw_data_worksheet(self, google_config: dict, wb: gspread.Spreadsheet) -> tuple:
        # Upload raw data sheet

        raw_data_ws_name = google_config.get('raw data worksheet name')
        if not raw_data_ws_name:
            return False, 'Google Sheets Error', 'The "raw data worksheet name" key is missing in config.json file.'

        success, message, ws_raw_data = self.__open_sheet(wb, raw_data_ws_name)
        if not (success and ws_raw_data):
            self.__clean_up()
            return False, 'Google Sheets Error', message

        self.__create_raw_data_list()

        success, message = self.__remove_data_and_formatting(wb, ws_raw_data)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        # The order below matters: (1) resize the sheet, (2) format the sheet, (3) enter the data
        # The barcode column must be set to TEXT number format before the data is entered,
        #   otherwise any leading zeros will be lost.
        num_rows = 1
        num_cols = 1
        if len(self.__raw_data_list) > 0:
            num_rows = len(self.__raw_data_list)
            num_cols = len(self.__raw_data_list[0])

        success, message = self.__resize_sheet(ws_raw_data, num_rows, num_cols)
        if not success:
            return False, 'Google Sheets Error', message

        success, message = self.__format_raw_data_sheet(wb, ws_raw_data)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

        success, message = self.__enter_data_on_sheet(ws_raw_data, self.__raw_data_list)
        if not success:
            self.__clean_up()
            return False, 'Google Sheets Error', message

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

    def __create_raw_data_list(self) -> None:
        success, message, raw_data = self.__db_manager.get_all_activity_table_data()

        self.__raw_data_list = [['Last Name', 'First Name', 'Barcode', 'Checkin', 'Checkout', 'Hours']]
        for tpl in raw_data:
            self.__raw_data_list = self.__raw_data_list + [list(tpl)]

    def __get_google_config(self) -> tuple:
        """
        This *private* method gets the configuration data in order to open the Google Sheet.

        :return: success, message, config info
        """

        config_file = os.path.join(THIS_DIRECTORY, CONFIG_FILENAME)

        # Check if the google config file exists.
        if not os.path.isfile(config_file):
            return False, 'The config.json file does not exist.', {}

        # Open the files if it exists.
        with open(config_file, 'r') as fh:
            try:
                # Read the json string from the file into the config dictionary.
                config = json.load(fh)

                # Store the google config dictionary
                google_config = config.get('google config')
                if not google_config:
                    return False, 'The "google config" key is missing in config.json file.', {}

                return True, '', google_config

            except Exception as e:
                return False, 'The config.json file is unreadable.', {}

    def __open_spreadsheet(self, google_config: dict) -> tuple:
        """
        This *private* method opens the Google Spreadsheet.

        :param google_config: the google config dictionary to open the Google Spreadsheet
        :return: wb = Google Spreadsheet file
        """
        try:
            # See the gspread documentation to open a Google Sheet
            service_account = google_config.get('service account')
            if not service_account:
                return False, 'The "service account" key is missing in config.json file.', None

            folder, file = os.path.split(service_account)
            credential_file = os.path.join(THIS_DIRECTORY, folder, file)

            gspread_client = gspread.service_account(credential_file)
            spreadsheet_url = google_config.get('spreadsheet url')
            if not spreadsheet_url:
                return False, 'The "spreadsheet url" key is missing in config.json file.', None

            wb = gspread_client.open_by_url(spreadsheet_url)

            return True, '', wb
        except Exception as e:
            return False, 'There was an error with the Google Sheets file.', None

    def __check_spreadsheet(self, wb: gspread.Spreadsheet, google_config: dict) -> None:
        worksheet_exists = False
        raw_data_worksheet_exists = False

        for worksheet in wb.worksheets():
            if worksheet.title == google_config.get('worksheet name'):
                worksheet_exists = True
            elif worksheet.title == google_config.get('raw data worksheet name'):
                raw_data_worksheet_exists = True

        if not worksheet_exists:
            wb.add_worksheet(google_config.get('worksheet name'), 1, 1)
        if not raw_data_worksheet_exists:
            wb.add_worksheet(google_config.get('raw data worksheet name'), 1, 1)

    def __open_sheet(self, wb: gspread.Spreadsheet, ws_name: str) -> tuple:
        """
        This *private* method opens the Google Sheet.

        :param wb: Google Spreadsheet file
        :param ws_name: Worksheet name
        :return: ws = one Worksheet in the file
        """
        try:
            # See the gspread documentation to open a Google Sheet
            ws = wb.worksheet(ws_name)
            return True, '', ws
        except Exception as e:
            return False, 'There was an error with the Google Sheets file.', None

    def __remove_data_and_formatting(self, wb: gspread.Spreadsheet, ws: gspread.Worksheet) -> tuple:
        """
        This *private* method removes all data and formatting from the sheet.
        Without this, when new rows and columns are added, the format from the existing cells is used.

        :param wb: the Google Spreadsheet file
        :param ws: the one Google Worksheet in the file
        :return: None
        """

        # See the Google Sheets API and gspread documentation for help
        sheet_id = ws._properties.get('sheetId')
        if not sheet_id:
            return False, 'There was an error removing the previous data and formatting from the Google Sheet.'

        lst = []

        # Clear all formatting on the sheet
        lst.append(self.__clear_formatting(sheet_id))

        if ws.col_count > 0:
            # Reset the column width to 100 pixels (default) so that new columns are added with this default size.
            lst.append(self.__set_column_width(sheet_id, 0, ws.col_count, 100))

        if ws.row_count > 0:
            # Reset the row height to 21 pixels (default) so that new rows are added with this default size.
            lst.append(self.__set_row_height(sheet_id, 0, ws.row_count, 21))

        # Unfreeze rows and columns
        lst.append(self.__set_frozen_rows(sheet_id, 0))
        lst.append(self.__set_frozen_columns(sheet_id, 0))

        # Clear any filters
        lst.append(self.__clear_filter(sheet_id))

        try:
            # Clear all data on the sheet
            # ws.clear() cannot be completed with a ws.batch_update() call, so it is done separate
            response = ws.clear()

            if len(lst) > 0:
                body = {'requests': lst}
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
        sheet_id = ws._properties.get('sheetId')
        if not sheet_id:
            return False, 'There was an error formatting the WorkSheet.'

        lst = []
        if num_rows > 0 and num_cols > 3:
            # A1:D1 - Set the cell background color and text to bold
            lst.append(self.__set_background_color(sheet_id, 0, 1, 0, 4, 217/255, 210/255, 233/255))
            lst.append(self.__set_text_format(sheet_id, 0, 1, 0, 4, True, False, False))

            # A1:C? - Set the horizontal alignment to LEFT
            lst.append(self.__set_number_format(sheet_id, 0, num_rows, 0, 3, 'TEXT'))
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, num_rows, 0, 3, 'LEFT'))

            # D1:D? - Set the horizontal alignment to RIGHT
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, num_rows, 3, 4, 'RIGHT'))

        if num_rows > 1 and num_cols > 3:
            # D2:D? - Set number format to NUMBER with 2 decimal places
            lst.append(self.__set_number_format(sheet_id, 1, num_rows, 3, 4, 'NUMBER', '0.00'))

        if num_rows > 0 and num_cols > 4:
            # E1:?1 - Set background color, horizontal alignment, number format, and bold.
            lst.append(self.__set_background_color(sheet_id, 0, 1, 4, num_cols, 201/255, 218/255, 248/255))
            lst.append(self.__set_text_format(sheet_id, 0, 1, 4, num_cols, True, False, False))
            lst.append(self.__set_number_format(sheet_id, 0, 1, 4, num_cols, 'DATE', 'm"/"d'))
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, 1, 4, num_cols, 'CENTER'))

        if num_rows > 1 and num_cols > 4:
            # E2:?? - Set horizontal alignment to CENTER and number format to NUMBER with 2 decimals.
            lst.append(self.__set_number_format(sheet_id, 1, num_rows, 4, num_cols, 'NUMBER', '0.00'))
            lst.append(self.__set_horizontal_alignment(sheet_id, 1, num_rows, 4, num_cols, 'CENTER'))

        if num_cols > 3:
            # Columns A:D - Set the width to 100 pixels (default)
            lst.append(self.__set_column_width(sheet_id, 0, 4, 100))

        if num_cols > 4:
            # Columns E:? - Set the width to 50 pixels
            lst.append(self.__set_column_width(sheet_id, 4, num_cols, 50))

        if num_rows > 0:
            # Rows 1:? - Set the height to 21 pixels (default)
            lst.append(self.__set_row_height(sheet_id, 0, num_rows, 21))

        if num_rows > 1:
            # Row 1 and Columns A:D - Set to frozen
            lst.append(self.__set_frozen_rows(sheet_id, 1))

        if num_cols > 4:
            # Row 1 and Columns A:D - Set to frozen
            lst.append(self.__set_frozen_columns(sheet_id, 4))

        try:
            if len(lst) > 0:
                body = {'requests': lst}
                wb.batch_update(body)
            return True, ''
        except Exception as e:
            return False, 'There was an error formatting the WorkSheet.'

    def __format_raw_data_sheet(self, wb: gspread.Spreadsheet, ws: gspread.Worksheet) -> tuple:
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
        sheet_id = ws._properties.get('sheetId')
        if not sheet_id:
            return False, 'There was an error formatting the Raw Data Sheet.'

        lst = []
        if num_rows > 0 and num_cols > 2:
            # Cells A1:C? - Set number format to TEXT and horizontal alignment to LEFT
            lst.append(self.__set_number_format(sheet_id, 0, num_rows, 0, 3, 'TEXT'))
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, num_rows, 0, 3, 'LEFT'))

        if num_rows > 0 and num_cols > 4:
            # Columns D:E - Set horizontal alignment to LEFT
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, num_rows, 3, 5, 'LEFT'))

        if num_cols > 4:
            # Columns D:E - Set width to 200 pixels
            lst.append(self.__set_column_width(sheet_id, 3, 5, 200))

        if num_rows > 1 and num_cols > 4:
            # Cells D2:E? - Set background number format to DATE
            lst.append(self.__set_number_format(sheet_id, 1, num_rows, 3, 5, 'DATE', 'yyyy"-"mm"-"dd" "hh":"mm":"ss'))

        if num_rows > 0 and num_cols > 5:
            # Cells F1:F? - Set horizontal alignment to RIGHT
            lst.append(self.__set_horizontal_alignment(sheet_id, 0, num_rows, 5, 6, 'RIGHT'))

        if num_rows > 1 and num_cols > 5:
            # Cells F2:F? - Set number format to NUMBER with 2 decimals.
            lst.append(self.__set_number_format(sheet_id, 1, num_rows, 5, 6, 'NUMBER', '0.00'))

        try:
            if len(lst) > 0:
                body = {'requests': lst}
                wb.batch_update(body)
            return True, ''
        except Exception as e:
            return False, 'There was an error formatting the Raw Data Sheet.'

    def __set_column_width(self, sheet_id: int, start_index: int, end_index: int, pixel_size: int) -> dict:
        return {'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': start_index, 'endIndex': end_index},
            'properties': {'pixelSize': pixel_size},
            'fields': 'pixelSize'}}

    def __set_row_height(self, sheet_id: int, start_index: int, end_index: int, pixel_size: int) -> dict:
        return {'updateDimensionProperties': {
            'range': {'sheetId': sheet_id, 'dimension': 'ROWS', 'startIndex': start_index, 'endIndex': end_index},
            'properties': {'pixelSize': pixel_size},
            'fields': 'pixelSize'}}

    def __set_horizontal_alignment(self, sheet_id: int, start_row_index: int, end_row_index: int,
                                   start_column_index: int, end_column_index: int, alignment: str) -> dict:
        return {'repeatCell': {
            'range': {'sheetId': sheet_id,
                      'startRowIndex': start_row_index, 'endRowIndex': end_row_index,
                      'startColumnIndex': start_column_index, 'endColumnIndex': end_column_index},
            'cell': {
                'userEnteredFormat': {
                    'horizontalAlignment': alignment}},
            'fields': 'userEnteredFormat(horizontalAlignment)'}}

    def __set_number_format(self, sheet_id: int, start_row_index: int, end_row_index: int,
                            start_column_index: int, end_column_index: int, number_type: str, number_pattern: str = '') -> dict:
        return {'repeatCell': {
            'range': {'sheetId': sheet_id,
                      'startRowIndex': start_row_index, 'endRowIndex': end_row_index,
                      'startColumnIndex': start_column_index, 'endColumnIndex': end_column_index},
            'cell': {
                'userEnteredFormat': {
                    'numberFormat': {'type': number_type, 'pattern': number_pattern}}},
            'fields': 'userEnteredFormat(numberFormat)'}}

    def __set_text_format(self, sheet_id: int, start_row_index: int, end_row_index: int,
                          start_column_index: int, end_column_index: int,
                          is_bold: bool, is_italic: bool, is_underline: bool) -> dict:
        return {'repeatCell': {
            'range': {'sheetId': sheet_id,
                      'startRowIndex': start_row_index, 'endRowIndex': end_row_index,
                      'startColumnIndex': start_column_index, 'endColumnIndex': end_column_index},
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': is_bold, 'italic': is_italic, 'underline': is_underline}}},
            'fields': 'userEnteredFormat(textFormat)'}}

    def __set_background_color(self, sheet_id: int, start_row_index: int, end_row_index: int,
                               start_column_index: int, end_column_index: int,
                               red: float, green: float, blue: float) -> dict:
        return {'repeatCell': {
            'range': {'sheetId': sheet_id,
                      'startRowIndex': start_row_index, 'endRowIndex': end_row_index,
                      'startColumnIndex': start_column_index, 'endColumnIndex': end_column_index},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': red, 'green': green, 'blue': blue}}},
            'fields': 'userEnteredFormat(backgroundColor)'}}

    def __set_frozen_rows(self, sheet_id: int, rows: int) -> dict:
        return {'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {'frozenRowCount': rows}},
            'fields': 'gridProperties(frozenRowCount)'}}

    def __set_frozen_columns(self, sheet_id: int, columns: int) -> dict:
        return {'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {'frozenColumnCount': columns}},
            'fields': 'gridProperties(frozenColumnCount)'}}

    def __clear_formatting(self, sheet_id: int) -> dict:
        return {'updateCells': {
            'range': {'sheetId': sheet_id},
            'fields': 'userEnteredFormat'}}

    def __clear_filter(self, sheet_id: int) -> dict:
        return {'clearBasicFilter': {'sheetId': sheet_id}}

    def __enter_data_on_sheet(self, ws: gspread.Worksheet, data: list) -> tuple:
        """
        This *private* method enters the data into the worksheet.

        :param ws: the one Google Worksheet in the file
        :return:
        """

        try:
            response = ws.update('A1', data, raw=False)
            return True, ''
        except Exception as e:
            return False, 'There was an error entering the data on the Google Sheet.'

    def __clean_up(self):
        gc.enable()
        self.__student_names_and_barcode_list.clear()
        self.__student_hours_list.clear()
        self.__header_list.clear()
        self.__data_list.clear()
        self.__raw_data_list.clear()
        gc.collect()
