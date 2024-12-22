import gc
import sqlite3
import os
import bcrypt

from sqlite3 import Error
from datetime import datetime


class DatabaseManager:
    """This class manages all database operations."""

    def __init__(self, filename: str):
        self.__filename = filename
        self.__db_tables = ('student', 'activity', 'admin')
        self.__db_indexes = ('activity_id', )
        self.__db_triggers = ('insert_activity', 'update_activity',
                              'insert_student', 'update_student',
                              'insert_admin', 'update_admin', 'delete_admin')

    def logout_all(self) -> tuple:
        """This method will logout all active accounts with 0 hours."""

        success = False
        message = ''
        count = 0
        data = list()

        # Get a list
        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = '''SELECT id, checkin, checkout
                    FROM activity
                    WHERE checkout IS NULL'''

        success, message = self.__sql_execute(cursor, sql)
        if success:
            # data is a list of tuples: [('id', 'checkin', 'checkout'), .... ]
            #   where 'checkout' should be None
            success, message, data = self.__sql_fetchall(cursor)

        if success and len(data) > 0:
            for tpl in data:
                # success, message = self.checkout_student(tpl[0], tpl[1])
                sql = '''UPDATE activity SET checkout=?
                                WHERE id=? AND checkout IS NULL'''
                parameters = (tpl[1], tpl[0])
                success, message = self.__sql_execute(cursor, sql, parameters)

                if success:
                    count = count + 1

            message = 'Logged out ' + str(count) + ' / ' + str(len(data)) + ' accounts'
            if count < len(data):
                message = 'FAIL: ' + message
            else:
                message = 'SUCCESS: ' + message

        self.__delete_connection(cursor, db_conn)

        return success, message

    def checkin_student(self, barcode: str, checkin: str = 'NOW') -> tuple:
        """
        This method will *check in* a student.
        The insert_activity trigger prevents a student from being checked in twice.

        :param barcode: the barcode scanned
        :param checkin: the check in time (default is current time)
        :return: (1) was this successful? (2) explanation of failure
        """

        success = False
        message = ''

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # NOTE: the insert_activity trigger prevents a student from being checked in twice.
        if checkin == 'NOW':
            checkin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # record = (barcode, checkin, None)
        # success, message = self.new_record('activity', record)
        sql = 'INSERT INTO activity (id, checkin, checkout) VALUES (?, ?, ?)'
        parameters = (barcode, checkin, None)
        success, message = self.__sql_execute(cursor, sql, parameters)

        if success:
            message = 'Checked In.'
        else:
            message = 'NOT Checked In.'

        self.__delete_connection(cursor, db_conn)

        return success, message

    def checkout_student(self, barcode: str, checkout: str = 'NOW') -> tuple:
        """This method will check out a student. The student must be checked in already."""

        success = False
        message = ''

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Add the student to the activity table.
        if checkout == 'NOW':
            checkout = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = '''UPDATE activity SET checkout=?
                WHERE id=? AND checkout IS NULL'''
        parameters = (checkout, barcode)

        success, message = self.__sql_execute(cursor, sql, parameters)

        if success:
            success, message, total_hours = self.__total_hours(cursor, barcode)
            message = f'Checked out. Total hours: {total_hours:.2f}'
        else:
            success, message, total_hours = self.__total_hours(cursor, barcode)
            message = f'NOT Checked out. Total hours: {total_hours:.2f}'

        self.__delete_connection(cursor, db_conn)

        return success, message

    def new_record(self, table: str, record: tuple) -> tuple:
        """
        This method adds a new record into a table.

        :param table: the name of the table in the database
        :param record: a tuple containing the new record, but without a rowid
        :return: (1) was this successful? (2) explanation of failure
        """

        success = False
        message = ''
        table = table.lower()

        if not (table in self.__db_tables):
            return False, 'Invalid table'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = ''
        if table == 'student':
            sql = 'INSERT INTO student (id, firstname, lastname) VALUES (?, ?, ?)'
        elif table == 'activity':
            sql = 'INSERT INTO activity (id, checkin, checkout) VALUES (?, ?, ?)'
        elif table == 'admin':
            # encrypt the pin, then replace the pin with the encrypted pin in the record
            pin = self.__encrypt_pin(record[3])
            record = record[0:3] + (pin, )
            sql = 'INSERT INTO admin (id, firstname, lastname, pin) VALUES (?, ?, ?, ?)'
        parameters = record

        success, message = self.__sql_execute(cursor, sql, parameters)
        self.__delete_connection(cursor, db_conn)

        return success, message

    def check_barcode(self, barcode: str) -> tuple:
        """
        This method checks if a barcode is valid.

        :param barcode: the barcode scanned
        :return: (1) was this successful? (2) explanation of failure (3) 'Invalid', 'Student', or 'Admin'
        """

        success = False
        message = ''
        barcode_type = 'Invalid'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', 'Error'

        # Check if the student table contains a student with this barcode.
        sql = 'SELECT id, firstname, lastname FROM student WHERE id=?'
        parameters = (barcode,)
        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchall(cursor)
            if len(data) > 0:
                barcode_type = 'Student'

        if barcode_type == 'Invalid':
            # Check if the admin table contains an admin with this barcode.
            sql = 'SELECT id, firstname, lastname, pin FROM admin WHERE id=?'
            parameters = (barcode,)
            success, message = self.__sql_execute(cursor, sql, parameters)
            if success:
                success, message, data = self.__sql_fetchone(cursor)
                if len(data) > 0:
                    barcode_type = 'Admin'

        self.__delete_connection(cursor, db_conn)

        return success, message, barcode_type

    def check_pin(self, barcode: str, pin: str) -> tuple:
        """
        This method checks if an admin pin is correct.

        :param barcode: the barcode scanned
        :param pin: the admin pin (not encrypted)
        :return: (1) was this successful? (2) explanation of failure (3) was pin valid?
        """

        success = False
        message = ''
        valid = False

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', False

        # Check if the admin table contains an admin with this barcode.
        sql = 'SELECT pin FROM admin WHERE id=?'
        parameters = (barcode, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchone(cursor)
            if len(data) > 0 and self.__is_pin_correct(pin, data[0]):
                valid = True

        self.__delete_connection(cursor, db_conn)

        return success, message, valid

    def get_student_data(self, barcode: str) -> tuple:
        """
        This method returns a student name, checked in/out status, and total hours worked.

        :param barcode: the barcode scanned
        :return: a 3-tuple: ( success, message, (firstname, lastname, status, total_hours) )
        """

        success = False
        message = ''

        first_name = ''
        last_name = ''
        status = ''
        total_hours = 0.0

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', ()

        # Get the student name from the student table.
        success, message, first_name, last_name = self.__get_student_name(cursor, barcode)

        if success:
            # Get the student status (Checked In or Checked Out).
            success, message, status = self.__get_student_status(cursor, barcode)

            if success:
                # Get the total hours worked.
                success, message, total_hours = self.__total_hours(cursor, barcode)

        self.__delete_connection(cursor, db_conn)

        return success, message, (first_name, last_name, status, total_hours)

    def __get_student_name(self, cursor: sqlite3.Cursor, barcode: str) -> tuple:
        """
        Get the student's first name and last name using the barcode.

        :param cursor: the cursor object used to execute sql statements
        :param barcode: the barcode scanned
        :return: a 4-tuple: (success, message, first_name, last_name)
        """
        first_name = ''
        last_name = ''
        sql = 'SELECT firstname, lastname FROM student WHERE id=?'
        parameters = (barcode,)
        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchone(cursor)
            if success and len(data) > 1:
                first_name = data[0]
                last_name = data[1]

        return success, message, first_name, last_name

    def __get_student_status(self, cursor: sqlite3.Cursor, barcode: str) -> tuple:
        """
        Get the status of the student ('Checked In' or 'Checked Out').

        :param cursor: the cursor object used to execute sql statements
        :param barcode: the barcode scanned
        :return: a 3-tuple: (success, message, status)
        """
        status = ''
        sql = '''SELECT rowid, id, checkin, checkout FROM activity 
                WHERE id=? AND checkout IS NULL'''
        parameters = (barcode, )
        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchone(cursor)
            if success and data:
                status = 'Checked In'
            elif success and not data:
                status = 'Checked Out'

        return success, message, status

    def get_student_hours_table(self, barcode: str) -> tuple:
        """This method returns a list of the hours for a student, totaled for each day."""

        success = False
        message = ''

        hours_table = list()
        total_hours = 0
        checked_in_data = tuple()
        data = list()

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', (), 0

        # First see if the student is checked in and get those hours.
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = '''SELECT DATE(checkin),
                ROUND(SUM(JULIANDAY(?) - JULIANDAY(checkin)) * 24.0, 2)
                FROM activity WHERE id=? AND checkout IS NULL'''
        parameters = (current_time, barcode)
        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, checked_in_data = self.__sql_fetchone(cursor)
            if checked_in_data == (None, None):
                checked_in_data = ()

        sql = '''SELECT DATE(checkin),
                ROUND(SUM(JULIANDAY(checkout) - JULIANDAY(checkin)) * 24.0, 2)
                FROM activity WHERE id=? AND checkout IS NOT NULL
                GROUP BY DATE(checkin) ORDER BY DATE(checkin) DESC'''
        parameters = (barcode, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchall(cursor)

            if checked_in_data:
                # data.insert(0, checked_in_data)
                if data:
                    if checked_in_data[0] == data[0][0]:
                        checked_in_data = (data[0][0], checked_in_data[1] + data[0][1])
                        data.pop(0)

                data.insert(0, checked_in_data)

            # This will create the table of hours, which is a list of 3-tuples
            # [ ('day of week', 'date', 'hours'), ... ]
            hours_table = list()
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for (date, hours) in data:
                # Convert the date string to a datetime object to determine the day of the week.
                day_of_week = days[datetime.strptime(date, '%Y-%m-%d').weekday()]
                hours_table.append((day_of_week, date, f'{hours:5.2f}'))

            total_hours = 0.0
            for item in hours_table:
                total_hours += float(item[2])

        self.__delete_connection(cursor, db_conn)

        return success, message, hours_table, total_hours

    def get_checked_in_list(self) -> tuple:
        """
        This method returns a list of students currently checked in.
        :return: list of 3-tuples [ (id, firstname, lastname), ... ]
        """

        success = False
        message = ''

        data = list()
        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', list()

        sql = '''SELECT student.id, student.firstname, student.lastname
                        FROM student JOIN activity ON student.id=activity.id
                        WHERE activity.checkout IS NULL
                        ORDER BY student.lastname ASC, student.firstname ASC'''

        success, message = self.__sql_execute(cursor, sql)
        if success:
            # data is a list of tuples: [('id', 'firstname', 'lastname'), .... ]
            success, message, data = self.__sql_fetchall(cursor)

        self.__delete_connection(cursor, db_conn)

        return success, message, data

    def get_all_activity_table_data(self) -> tuple:
        """
        This method returns a list of all records in the activity table.
        :return: list of 5-tuples [ (lastname, firstname, id, checkin, checkout, hours), ... ]
        """

        success = False
        message = ''

        data = list()
        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', list()

        sql = '''SELECT student.lastname, student.firstname, student.id, activity.checkin, activity.checkout,
                        ROUND((JULIANDAY(activity.checkout) - JULIANDAY(activity.checkin)) * 24.0, 2) hours
                        FROM student JOIN activity ON student.id=activity.id
                        WHERE checkout IS NOT NULL
                        ORDER BY activity.checkin ASC'''

        success, message = self.__sql_execute(cursor, sql)
        if success:
            # data is a list of tuples: [ (lastname, firstname, id, checkin, checkout, hours), .... ]
            success, message, data = self.__sql_fetchall(cursor)

        self.__delete_connection(cursor, db_conn)

        return success, message, data

    def get_google_sheet_data(self) -> tuple:
        """This method uploads the student data to a Google Sheet."""

        success = False
        message = ''

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', [], []

        success, message, student_names_and_barcode_list = self.__get_student_names_and_barcode_list(cursor)
        if not success:
            return False, 'Error with student names and barcode list', [], []

        success, message, student_hours_list = self.__get_student_hours_list(cursor)
        if not success:
            return False, 'Error with student hours list', [], []

        self.__delete_connection(cursor, db_conn)

        return True, 'Successfully retrieved data', student_names_and_barcode_list, student_hours_list

    def __get_student_names_and_barcode_list(self, cursor: sqlite3.Cursor) -> tuple:
        """
        This *private* method is called by the upload_student_data_to_google_sheet() method to pass
        the complete list of student names and barcodes to the GoogleSheetManager.

        :param cursor: the cursor object used to execute sql statements
        :return: success, message, student_names_and_barcode_list
        """
        # "student_names_and_barcode_list" will be a list of tuples: [ (lastname, firstname, barcode), ... ]
        sql = '''SELECT lastname, firstname, id FROM student 
                ORDER BY lastname ASC, firstname ASC, id ASC'''
        self.__sql_execute(cursor, sql)
        success, message, student_names_and_barcode_list = self.__sql_fetchall(cursor)
        if not success:
            return success, message, None
        return success, message, student_names_and_barcode_list

    def __get_student_hours_list(self, cursor: sqlite3.Cursor) -> tuple:
        """
        This *private* method is called by the upload_student_data_to_google_sheet() method to pass
        the complete list of student hours (grouped by barcode and week) to the GoogleSheetManager.

        :param cursor: the cursor object used to execute sql statements
        :return: success, message, student_hours_list
        """
        # https://www.sqlite.org/lang_datefunc.html
        # %Y  year: 0000-9999
        # %W  week of year: 00-53, the first Monday is the beginning of week 1.
        # By default, STRFTIME('%W') uses Monday as the first day of the week, but we want Sunday to be first.
        #   So the modifiers '-6 days' and 'weekday 0' will return the date of the Sunday at the start of the week.
        #   The CASE is used because STRFTIME('%W') is correct if Jan 1 is Monday, otherwise it is off by 1.
        sql = '''SELECT student.lastname, student.firstname, student.id, 
                STRFTIME('%Y', activity.checkin, '-6 days', 'weekday 0') year,
                CASE
                    WHEN STRFTIME('%j', activity.checkin, '-6 days', 'weekday 0') % 7 == 0
                        THEN STRFTIME('%W', activity.checkin, '-6 days', 'weekday 0') 
                    ELSE STRFTIME('%W', activity.checkin, '-6 days', 'weekday 0') + 1
                    END week,
                SUM(ROUND( (JULIANDAY(activity.checkout) - JULIANDAY(activity.checkin)) * 24.0, 2)) hours
                FROM student JOIN activity
                ON student.id = activity.id
                WHERE activity.checkout IS NOT NULL
                GROUP BY student.id, year, week
                ORDER BY student.lastname ASC, student.firstname ASC, year ASC, week ASC'''
        self.__sql_execute(cursor, sql)

        # "student_hours_list" is a list of tuples: [ (lastname, firstname, barcode, year, week number, week hours),...]
        # Note: there is one tuple for each week that a student has logged hours,
        #   so each student will have several tuples with each tuple indicating weekly hours.
        success, message, student_hours_list = self.__sql_fetchall(cursor)
        if not success:
            return success, message, None
        return success, message, student_hours_list

    def __create_connection(self) -> tuple:
        """
        This *private* method establishes a connection to the database and creates a cursor.

        :return: (database connection, database cursor)
        """

        # Garbage collection slows down the process, so disable it temporarily.
        # Garbage collection is enabled again in the __delete_connection() method.
        gc.disable()

        db_conn = None
        cursor = None

        # Check if the database exists, do not create one if it does not exist.
        if os.path.isfile(self.__filename):

            try:
                # Connect to the database, if the database exists.
                # If the database does not exist, the database is created but with no tables, indexes, triggers, etc.
                db_conn = sqlite3.connect(self.__filename, isolation_level=None)
                try:
                    cursor = db_conn.cursor()
                except Error:
                    cursor = None
                    db_conn.close()  # close the database connection if the cursor creation failed
            except Error:
                db_conn = None

        return db_conn, cursor

    def __delete_connection(self, cursor: sqlite3.Cursor, db_conn: sqlite3.Connection) -> None:
        """
        This *private* method closes the database connection and cursor.

        :param cursor: the cursor object used to execute sql statements
        :param db_conn: the database connection
        :return: None
        """

        gc.enable()

        try:
            cursor.close()
            try:
                db_conn.close()
            except Error:
                db_conn = None
        except Error:
            cursor = None

        gc.collect()

    def __sql_execute(self, cursor: sqlite3.Cursor, sql: str, parameters: tuple = None) -> tuple:
        """
        This *private* method is the **ONLY** way to execute sql statements on the database.
        DO **NOT** use any other cursor.execute() methods.

        :param cursor: the cursor object used to execute sql statements
        :param sql: the sql statement to execute
        :param parameters: the parameters of the sql statement
        :return: (boolean, string)
        """
        success = False
        message = ''
        try:
            cursor.execute('PRAGMA foreign_keys=ON')
            if parameters:
                cursor.execute(sql, parameters)
            else:
                cursor.execute(sql)
            success = True
        except Error as e:
            success = False
            message = str(e)

        return success, message

    def __sql_fetchall(self, cursor: sqlite3.Cursor) -> tuple:
        """
        This *private* method fetches all the records from the database after the previously executed sql statement.
        This method returns a 3-tuple:
        (1) boolean indicating if the sql statement was executed successfully
        (2) string with a message indicating reason for failure
        (3) list of tuples containing the data fetched from the database

        :param cursor: the cursor pointing to the database
        :return: (boolean, string, list of tuples)
        """
        # 6/28/21 - added if statement to return empty list if no records are returned

        success = False
        message = ''
        data = list()
        try:
            # WARNING: Make sure data is not None after the call
            data = cursor.fetchall()
            if not data:
                data = list()
            success = True
        except Error as e:
            data = list()
            success = False
            message = str(e)

        return success, message, data

    def __sql_fetchone(self, cursor: sqlite3.Cursor) -> tuple:
        """
        This *private* method fetches one of the records from the database after the previously executed sql statement.
        This method returns a 3-tuple:
        (1) boolean indicating if the sql statement was executed successfully
        (2) string with a message indicating reason for failure
        (3) tuple containing the data fetched from the database

        :param cursor: the cursor pointing to the database
        :return: (boolean, string, tuple)
        """
        # 6/28/21 - added if statement to return empty tuple if no records are returned

        success = False
        message = ''
        data = tuple()
        try:
            # WARNING: Make sure data is not None after the call
            data = cursor.fetchone()
            if not data:
                data = tuple()
            success = True
        except Error as e:
            data = tuple()
            success = False
            message = str(e)

        return success, message, data

    def __total_hours(self, cursor: sqlite3.Cursor, barcode: str) -> tuple:
        total_hours = 0.0

        # Sum the total hours logged from previous checkins and checkouts.
        sql = '''SELECT SUM(JULIANDAY(checkout) - JULIANDAY(checkin)) * 24.0
                FROM activity WHERE id=? AND checkout IS NOT NULL'''
        parameters = (barcode, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        if not success:
            return success, message, 0.0

        success, message, data = self.__sql_fetchone(cursor)
        if not success:
            return success, message, 0.0

        if data and data[0]:
            total_hours = round(float(data[0]), 2)

        return success, message, total_hours

    def __is_pin_correct(self, raw_pin: str, encrypted_pin: str) -> bool:
        """
        This *private* method checks if the pin is correct.

        :param raw_pin: the raw unencrypted pin
        :param encrypted_pin: the encrypted pin
        :return: True if the pin is correct
        """
        return bcrypt.checkpw(str(raw_pin).encode(), str(encrypted_pin).encode())

    def __encrypt_pin(self, pin: str) -> str:
        """
        This *private* method encrypts the pin.

        :param pin: the raw unencrypted pin
        :return: the encrypted pin
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pin.encode(), salt)

        return hashed.decode()

    def create_database(self) -> tuple:
        """
        This method creates the database and tables if they do not exist.

        :return: Boolean indicating success, String explaining success/fail
        """

        gc.disable()

        db_conn = None
        cursor = None
        total = len(self.__db_tables) + len(self.__db_indexes) + len(self.__db_triggers)

        # Check if the database files exists.
        if os.path.isfile(self.__filename):
            return False, 'Database file already exists', 0, total

        # The self.__create_connection() cannot be used here because that method does not allow
        # a blank database to be created.
        # db_conn, cursor = self.__create_connection()

        try:
            # Connect to the database, if the database exists.
            # If the database does not exist, the database is created but with no tables, indexes, triggers, etc.
            db_conn = sqlite3.connect(self.__filename, isolation_level=None)
            try:
                cursor = db_conn.cursor()
            except Error:
                cursor = None
                db_conn.close()  # close the database connection if the cursor creation failed
        except Error:
            db_conn = None

        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', 0, total

        counter = 0
        # Create the tables, indexes, and triggers
        for table in self.__db_tables:
            success, message = self.__create_db_object(cursor, 'table', table)
            if success:
                counter += 1

        for index in self.__db_indexes:
            success, message = self.__create_db_object(cursor, 'index', index)
            if success:
                counter += 1

        for trigger in self.__db_triggers:
            success, message = self.__create_db_object(cursor, 'trigger', trigger)
            if success:
                counter += 1

        # Add a default admin account.
        # success, message, data = self.get_table('admin')
        # if success and len(data) == 0:
        #     self.new_record('admin', ('4237', 'Sir', 'Lance-A-Bot', '4237'))
        # self.new_record('admin', ('4237', 'Sir', 'Lance-A-Bot', '4237'))

        # encrypt the pin, then replace the pin with the encrypted pin in the record
        record = ('4237', 'Sir', 'Lance-A-Bot', '4237')
        pin = self.__encrypt_pin(record[3])
        record = record[0:3] + (pin,)
        sql = 'INSERT INTO admin (id, firstname, lastname, pin) VALUES (?, ?, ?, ?)'
        parameters = record
        success, message = self.__sql_execute(cursor, sql, parameters)

        self.__delete_connection(cursor, db_conn)

        total = len(self.__db_tables) + len(self.__db_indexes) + len(self.__db_triggers)
        if total == counter:
            return True, 'All database objects created', counter, total
        else:
            return False, 'Not all database objects created', counter, total

    def __create_db_object(self, cursor: sqlite3.Cursor, type: str, name: str) -> tuple:
        """This method checks if the table/index/trigger exists and creates the object if it does not exist."""

        # Check if the object is in the database files. Create the table if it does not exist.
        sql = f'SELECT name FROM sqlite_master WHERE type="{type}" AND name="{name}"'
        self.__sql_execute(cursor, sql)

        success, message, data = self.__sql_fetchall(cursor)
        if data:
            return False, 'The ' + name + ' ' + type + ' already exists.'

        sql = ''
        if type == 'table':
            if name == 'student':
                sql = self.__create_student_table()
            elif name == 'activity':
                sql = self.__create_activity_table()
            elif name == 'admin':
                sql = self.__create_admin_table()

        elif type == 'index':
            if name == 'activity_id':
                sql = self.__create_activity_id_index()

        elif type == 'trigger':
            if name == 'insert_student':
                sql = self.__create_insert_student_trigger()
            elif name == 'update_student':
                sql = self.__create_update_student_trigger()
            elif name == 'insert_activity':
                sql = self.__create_insert_activity_trigger()
            elif name == 'update_activity':
                sql = self.__create_update_activity_trigger()
            elif name == 'insert_admin':
                sql = self.__create_insert_admin_trigger()
            elif name == 'update_admin':
                sql = self.__create_update_admin_trigger()
            elif name == 'delete_admin':
                sql = self.__create_delete_admin_trigger()

        else:
            return False, 'Database object was NOT created.'

        if sql:
            success, message = self.__sql_execute(cursor, sql)
            return success, message


    def __create_student_table(self):
        # Why is the Primary Key also specified as NOT NULL?
        #   Non-integer Primary Keys can be set to NULL in sqlite.
        sql = '''CREATE TABLE IF NOT EXISTS student
                (id TEXT PRIMARY KEY NOT NULL, 
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL)'''
        return sql

    def __create_activity_table(self):
        # Why are the checkin and checkout columns TEXT rather than INTEGER?
        #   Sqlite uses a dynamic data type system, unlike other databases that use a static data type system.
        #   So the column data types are only a suggestion (not a requirement).
        #   The checkin and checkout fields are stored using the SQLite command: DATETIME("NOW", "LOCALTIME")
        #     which returns the current date and time in the string format "YYYY-MM-DD HH:MM:SS"
        # The CHECK(... GLOB ...) constraint validates the required format for the checkin and checkout fields.
        # The ON DELETE and ON UPDATE actions for the FOREIGN KEY (id) will handle what to do with records in
        #   the Activity table when the corresponding id in the Student table is deleted or updated.
        date_time_format = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'
        sql = f'''CREATE TABLE IF NOT EXISTS activity
                (id TEXT NOT NULL,
                checkin TEXT NOT NULL CHECK(checkin GLOB "{date_time_format}"),
                checkout TEXT CHECK(checkout GLOB "{date_time_format}"),
                FOREIGN KEY (id) REFERENCES student(id) ON DELETE CASCADE ON UPDATE CASCADE)'''
        return sql

    def __create_admin_table(self):
        # Why is the Primary Key also specified as NOT NULL?
        #   Non-integer Primary Keys can be set to NULL -- its a known sqlite bug.
        sql = '''CREATE TABLE IF NOT EXISTS admin
                (id TEXT PRIMARY KEY NOT NULL, 
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                pin TEXT NOT NULL)'''
        return sql

    def __create_activity_id_index(self):
        sql = '''CREATE INDEX IF NOT EXISTS activity_id ON activity(id)'''
        return sql

    def __create_insert_student_trigger(self):
        # This trigger runs before a new record is inserted in the Student table.
        #   It checks if the NEW id is already in the Admin table. If the NEW id already exists in the Admin
        #   table, then the insert is aborted.
        message = 'Barcode already exists in the Admin Table. Use a different Barcode.'
        condition = '(SELECT COUNT(*) FROM admin WHERE NEW.id=id) >0'
        sql = f'''CREATE TRIGGER IF NOT EXISTS insert_student BEFORE INSERT ON student
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_update_student_trigger(self):
        # This trigger runs before a record is updated in the Student table.
        #   It checks if the NEW id is already in the Admin table. If the NEW id already exists in the Admin
        #   table, then the update is aborted.
        message = 'Barcode already exists in the Admin Table. Use a different Barcode.'
        condition = '(SELECT COUNT(*) FROM admin WHERE NEW.id=id) >0'
        sql = f'''CREATE TRIGGER IF NOT EXISTS update_student BEFORE UPDATE OF id ON student
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_insert_activity_trigger(self):
        # This trigger runs before a new record is inserted in the Activity table.
        #   It will only allow a student to be "Checked In" one time. If the new checkout time is NULL
        #   and there already exists a NULL checkout time for that id, then the insert is aborted.
        message = 'Student already Checked In. Must include a Check Out time.'
        condition = '(SELECT COUNT(*) FROM activity WHERE NEW.id=id AND NEW.checkout IS NULL AND checkout IS NULL) >0'
        sql = f'''CREATE TRIGGER IF NOT EXISTS insert_activity BEFORE INSERT ON activity
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_update_activity_trigger(self):
        # This trigger runs before a record is updated in the Activity table.
        #   It will only allow a student to be "Checked In" one time. If the updated checkout time is NULL
        #   and there already exists a NULL checkout time for that id, then the update is aborted.
        message = 'Student already Checked In. Must include a Check Out time.'
        condition = '''(SELECT COUNT(*) FROM activity 
                        WHERE NEW.rowid!=rowid AND NEW.id=id AND NEW.checkout IS NULL AND checkout IS NULL) >0'''
        sql = f'''CREATE TRIGGER IF NOT EXISTS update_activity BEFORE UPDATE ON activity
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_insert_admin_trigger(self):
        # This trigger runs before a new record is inserted in the Admin table.
        #   It checks if the NEW id is already in the Student table. If the NEW id already exists in the Student
        #   table, then the insert is aborted.
        message = 'Barcode already exists in the Student Table. Use a different Barcode.'
        condition = '(SELECT COUNT(*) FROM student WHERE NEW.id=id) >0'
        sql = f'''CREATE TRIGGER IF NOT EXISTS insert_admin BEFORE INSERT ON admin
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_update_admin_trigger(self):
        # This trigger runs before a record is updated in the Admin table.
        #   It checks if the NEW id is already in the Student table. If the NEW id already exists in the Student
        #   table, then the update is aborted.
        message = 'Barcode already exists in the Student Table. Use a different Barcode.'
        condition = '(SELECT COUNT(*) FROM student WHERE NEW.id=id) >0'
        sql = f'''CREATE TRIGGER IF NOT EXISTS update_admin BEFORE UPDATE OF id ON admin
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql

    def __create_delete_admin_trigger(self):
        # This trigger runs before a record is deleted in the Admin table.
        #   It checks if there only one admin in the Admin table.
        message = 'There must be at least one admin in the Admin Table.'
        condition = '(SELECT COUNT(*) FROM admin) =1'
        sql = f'''CREATE TRIGGER IF NOT EXISTS delete_admin BEFORE DELETE ON admin
                    BEGIN
                        SELECT CASE
                            WHEN {condition} THEN RAISE(ABORT, "{message}")
                        END;
                    END;'''
        return sql
