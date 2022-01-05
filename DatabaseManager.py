import sqlite3
from sqlite3 import Error
import os
from datetime import datetime
import bcrypt
import logging

from GoogleSheetManager import GoogleSheetManager

CONFIG_FILENAME = 'config.json'

logger = logging.getLogger('TimeTrack.DbManager')


class DatabaseManager:
    """This class manages all database operations."""

    def __init__(self, filename: str):
        self.__filename = filename
        self.__db_tables = ('student', 'activity', 'admin')
        self.__db_indexes = ('activity_id', )
        self.__db_triggers = ('insert_activity', 'update_activity',
                              'insert_student', 'update_student',
                              'insert_admin', 'update_admin', 'delete_admin')

    def login_user(self, barcode: str):
        user_data = tuple()

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', False

        # Check if the student table contains a student with this barcode.
        sql = 'SELECT rowid, id, firstname, lastname FROM student WHERE id=?'
        parameters = (barcode, )
        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchone(cursor)
            if len(data) > 0:
                user_data = ('student', ) + data

                # Get the status of the student ('Checked In' or 'Checked Out').
                sql = '''SELECT rowid, id, checkin, checkout FROM activity 
                        WHERE id=? AND checkout IS NULL'''
                parameters = (barcode,)
                success, message = self.__sql_execute(cursor, sql, parameters)
                if success:
                    success, message, data = self.__sql_fetchone(cursor)
                    if len(data) > 0:
                        user_data += ('Checked In', data[0], data[2])
                    else:
                        user_data += ('Checked Out', 0)
            else:
                # Check if the admin table contains an admin with this barcode.
                sql = 'SELECT rowid, id, firstname, lastname FROM admin WHERE id=?'
                parameters = (barcode,)
                success, message = self.__sql_execute(cursor, sql, parameters)
                if success:
                    success, message, data = self.__sql_fetchone(cursor)
                    if len(data) > 0:
                        user_data = ('admin', ) + data
                    else:
                        user_data = ('invalid', )

        self.__delete_connection(cursor, db_conn)

        return success, message, user_data

    def checkin_student(self, barcode: str, checkin: str = 'NOW'):
        """
        This method will *check in* a student.
        The insert_activity trigger prevents a student from being checked in twice.

        :param barcode: the barcode scanned
        :param checkin: the check in time (default is current time)
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'({barcode}, {checkin}) >> Started')

        # NOTE: the insert_activity trigger prevents a student from being checked in twice.
        if checkin == 'NOW':
            checkin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        record = (barcode, checkin, None)
        success, message = self.new_record('activity', record)
        if success:
            message = 'Checked In.'
        else:
            message = 'NOT Checked In.'

        return success, message

    def checkout_student(self, barcode: str, checkout: str = 'NOW'):
        """This method will check out a student. The student must be checked in already."""
        logger.debug(f'({barcode}) >> Started')
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

    def get_table(self, table: str, filter: str = ''):
        """
        This method returns the data from a table as a list of tuples, including the rowid.

        :param table: the name of the table to retrieve
        :param filter: used for the activity table only to filter by barcode (id)
        :return: (1) was this successful? (2) explanation of failure (3) the data
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        data = list()
        table = table.lower()

        if not self.__is_table_in_database(table):
            return False, 'Invalid table', data

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', data

        sql = ''
        parameters = None
        if table == 'student':
            sql = '''SELECT rowid, id, firstname, lastname FROM student ORDER BY id'''
        elif table == 'activity':
            if filter != '':
                sql = '''SELECT rowid, id, checkin, checkout FROM activity WHERE id=? ORDER BY checkin DESC'''
                parameters = (filter, )
            else:
                sql = '''SELECT rowid, id, checkin, checkout FROM activity ORDER BY checkin DESC'''
        elif table == 'admin':
            sql = '''SELECT rowid, id, firstname, lastname FROM admin ORDER BY id'''

        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchall(cursor)

        self.__delete_connection(cursor, db_conn)

        return success, message, data

    def get_record(self, table: str, row_id: int):
        """
        This method returns a list of records, including the rowid.
        The data is returned as a list of tuples.

        :param table: the name of the table in the database
        :param row_id: the row_id to fetch from the table
        :return: (1) was this successful? (2) explanation of failure (3) the data
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        data = list()
        table = table.lower()

        if not self.__is_table_in_database(table):
            return False, 'Invalid table', data

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', data

        sql = ''
        parameters = (row_id, )
        if table == 'student':
            sql = '''SELECT rowid, id, firstname, lastname FROM student WHERE rowid=?'''
        elif table == 'activity':
            sql = '''SELECT rowid, id, checkin, checkout FROM activity WHERE rowid=?'''
        elif table == 'admin':
            sql = '''SELECT rowid, id, firstname, lastname FROM admin WHERE rowid=?'''

        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchall(cursor)

        self.__delete_connection(cursor, db_conn)

        return success, message, data

    def new_record(self, table: str, record: tuple):
        """
        This method adds a new record into a table.

        :param table: the name of the table in the database
        :param record: a tuple containing the new record, but without a rowid
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        table = table.lower()

        if not self.__is_table_in_database(table):
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

    def edit_record(self, table: str, row_id: int, record: tuple):
        """
        This method edits a record in a table.

        :param table: the name of the table in the database
        :param row_id: the row_id to edit in the table
        :param record: a tuple containing the edited record, but without a rowid
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        table = table.lower()

        if not self.__is_table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = ''
        if table == 'student':
            sql = 'UPDATE student SET id=?, firstname=?, lastname=? WHERE rowid=?'
        elif table == 'activity':
            sql = 'UPDATE activity SET id=?, checkin=?, checkout=? WHERE rowid=?'
        elif table == 'admin':
            sql = 'UPDATE admin SET id=?, firstname=?, lastname=? WHERE rowid=?'

        parameters = record + (row_id, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        self.__delete_connection(cursor, db_conn)

        return success, message

    def edit_field(self, table: str, row_id: int, field: str, data: tuple):
        """
        This method edits a field in a table.

        :param table: the name of the table in the database
        :param row_id: the row_id to edit in the table
        :param: field: the name of the field to edit
        :param data: a tuple containing the edited field, but without a rowid
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        table = table.lower()

        if not self.__is_table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = ''
        if table == 'student':
            if field == 'id':
                sql = 'UPDATE student SET id=? WHERE rowid=?'
            if field == 'firstname':
                sql = 'UPDATE student SET firstname=? WHERE rowid=?'
            if field == 'lastname':
                sql = 'UPDATE student SET lastname=? WHERE rowid=?'
        elif table == 'activity':
            if field == 'id':
                sql = 'UPDATE activity SET id=? WHERE rowid=?'
            if field == 'checkin':
                sql = 'UPDATE activity SET checkin=? WHERE rowid=?'
            if field == 'checkout':
                sql = 'UPDATE activity SET checkout=? WHERE rowid=?'
        elif table == 'admin':
            if field == 'id':
                sql = 'UPDATE admin SET id=? WHERE rowid=?'
            if field == 'firstname':
                sql = 'UPDATE admin SET firstname=? WHERE rowid=?'
            if field == 'lastname':
                sql = 'UPDATE admin SET lastname=? WHERE rowid=?'

        parameters = data + (row_id, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        self.__delete_connection(cursor, db_conn)

        return success, message

    def delete_record(self, table: str, row_id: int):
        """
        This method deletes a record from a table.

        :param table: the name of the table in the database
        :param row_id: the row_id to edit in the table
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'() >> started')
        success = False
        message = ''
        table = table.lower()

        if not self.__is_table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = ''
        parameters = (row_id, )
        if table == 'student':
            sql = 'DELETE FROM student WHERE rowid=?'
        elif table == 'activity':
            sql = 'DELETE FROM activity WHERE rowid=?'
        elif table == 'admin':
            sql = 'DELETE FROM admin WHERE rowid=?'

        success, message = self.__sql_execute(cursor, sql, parameters)
        self.__delete_connection(cursor, db_conn)

        return success, message

    def check_barcode(self, barcode: str):
        """
        This method checks if a barcode is valid.

        :param barcode: the barcode scanned
        :return: (1) was this successful? (2) explanation of failure (3) 'Invalid', 'Student', or 'Admin'
        """
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''
        barcode_type = 'Invalid'

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', False

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

    def check_pin(self, barcode: str, pin: str):
        """
        This method checks if an admin pin is correct.

        :param barcode: the barcode scanned
        :param pin: the admin pin (not encrypted)
        :return: (1) was this successful? (2) explanation of failure (3) was pin valid?
        """
        logger.debug(f'({barcode}) >> Started')
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

    def reset_pin(self, row_id: int, new_pin: str, old_pin: str):
        """
        This method resets an admin pin.

        :param row_id: the row_id of the admin
        :param new_pin: the new admin pin (not encrypted)
        :param old_pin: the old admin pin (not encrypted)
        :return: (1) was this successful? (2) explanation of failure
        """
        logger.debug(f'() >> Started')
        success = False
        message = ''
        valid = False

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Check if the admin table contains an admin with this barcode.
        sql = 'SELECT pin FROM admin WHERE rowid=?'
        parameters = (row_id, )

        success, message = self.__sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.__sql_fetchone(cursor)
            if len(data) > 0:
                if self.__is_pin_correct(old_pin, data[0]):
                    sql = 'UPDATE admin SET pin=? WHERE rowid=?'
                    parameters = (self.__encrypt_pin(new_pin), row_id)
                    success, message = self.__sql_execute(cursor, sql, parameters)
                else:
                    success = False
                    message = 'Incorrect PIN.'

        self.__delete_connection(cursor, db_conn)

        return success, message

    def get_student_data(self, barcode: str) -> tuple:
        """
        This method returns a student name, checked in/out status, and total hours worked.

        :param barcode: the barcode scanned
        :return: a 3-tuple: ( success, message, (firstname, lastname, status, total_hours) )
        """
        logger.debug(f'({barcode}) >> Started')
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

    def get_total_hours(self, barcode: str):
        """This method returns the total hours for a student."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''

        total_hours = 0.0
        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', total_hours

        success, message, total_hours = self.__total_hours(cursor, barcode)

        self.__delete_connection(cursor, db_conn)

        return success, message, total_hours

    def get_student_hours_table(self, barcode: str):
        """This method returns a list of the hours for a student, totaled for each day."""
        logger.debug(f'({barcode}) >> Started')
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

    def get_checked_in_list(self):
        """
        This method returns a list of students currently checked in.
        :return: list of 3-tuples [ (id, firstname, lastname), ... ]
        """
        logger.debug('() >> Started')
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

    def upload_student_data_to_google_sheet(self) -> tuple:
        """This method uploads the student data to a Google Sheet."""

        logger.debug('() >> Started')
        success = False
        message = ''

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        success, message, student_names_and_barcode_list = self.__get_student_names_and_barcode_list(cursor)
        if not success:
            return False, 'Error with student names and barcode list'

        success, message, student_hours_list = self.__get_student_hours_list(cursor)
        if not success:
            return False, 'Error with student hours list'

        # The GoogleSheetManager automatically uploads the data when the object is created
        google_sheet_manager = GoogleSheetManager(student_names_and_barcode_list, student_hours_list)

        self.__delete_connection(cursor, db_conn)

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
        # By default, STRFTIME() uses Monday as the first day of the week,
        # so the modifier '+1 days' will change Sunday into the first day of the week.
        # ROUND(SUM(JULIANDAY(activity.checkout) - JULIANDAY(activity.checkin)) * 24.0, 2) hours
        sql = '''SELECT student.lastname, student.firstname, student.id, 
                STRFTIME('%Y', activity.checkin) year, STRFTIME('%W', activity.checkin, '+1 days') week, 
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

    def __create_connection(self):
        """
        This *private* method establishes a connection to the database and creates a cursor.

        :return: (database connection, database cursor)
        """
        db_conn = None
        cursor = None
        try:
            # Connect to the database, if the database exists.
            # If the database does not exist, the database is created but with no tables, indexes, triggers, etc.
            db_conn = sqlite3.connect(self.__filename, isolation_level=None)
            try:
                cursor = db_conn.cursor()
            except Error:
                cursor = None
                db_conn.close()  # close the database connection if the cursor creation failed
                logger.exception(' >> Error creating database cursor')
        except Error:
            db_conn = None
            logger.exception(' >> Error creating database connection')

        return db_conn, cursor

    def __delete_connection(self, cursor: sqlite3.Cursor, db_conn: sqlite3.Connection):
        """
        This *private* method closes the database connection and cursor.

        :param cursor: the cursor object used to execute sql statements
        :param db_conn: the database connection
        :return: None
        """
        # 6/28/21 - added if statements, should it be try-except?

        try:
            cursor.close()
            try:
                db_conn.close()
            except Error:
                db_conn = None
                logger.exception(' >> Error closing database connection')
        except Error:
            cursor = None
            logger.exception(' >> Error closing database cursor')

    def __sql_execute(self, cursor: sqlite3.Cursor, sql: str, parameters: tuple = None):
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
            logger.exception(f'{sql}, {parameters} >> Error with execute')
            success = False
            message = str(e)

        return success, message

    def __sql_fetchall(self, cursor: sqlite3.Cursor):
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
            logger.exception(f'() >> Error with fetchall.')
            data = list()
            success = False
            message = str(e)

        return success, message, data

    def __sql_fetchone(self, cursor: sqlite3.Cursor):
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
            logger.exception(f'() >> Error with fetchone.')
            data = tuple()
            success = False
            message = str(e)

        return success, message, data

    def __is_table_in_database(self, table: str):
        """
        This *private* method is used to check that the table is in the database.

        :param table: the name of the table to check for
        :return: True if the table is in the database
        """
        result = table.lower() in self.__db_tables
        if not result:
            logger.debug(f' >> Invalid table: {table}')
        return result

    def __total_hours(self, cursor: sqlite3.Cursor, barcode: str):
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

    def __is_pin_correct(self, raw_pin: str, encrypted_pin: str):
        """
        This *private* method checks if the pin is correct.

        :param raw_pin: the raw unencrypted pin
        :param encrypted_pin: the encrypted pin
        :return: True if the pin is correct
        """
        return bcrypt.checkpw(str(raw_pin).encode(), str(encrypted_pin).encode())

    def __encrypt_pin(self, pin: str):
        """
        This *private* method encrypts the pin.

        :param pin: the raw unencrypted pin
        :return: the encrypted pin
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pin.encode(), salt)

        return hashed.decode()

    def __check_database(self):
        """
        This method creates the database and tables if they do not exist.

        :return: None
        """
        logger.debug('() >> Started')

        # Check if the database files exists.
        if not os.path.isfile(self.__filename):
            logger.warning(f' >> File does not exist: {self.__filename} --> Creating the database file.')

        db_conn, cursor = self.__create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Check if the tables and indexes are created.
        for table in self.__db_tables:
            self.__check_db_object(cursor, 'table', table)

        for index in self.__db_indexes:
            self.__check_db_object(cursor, 'index', index)

        for trigger in self.__db_triggers:
            self.__check_db_object(cursor, 'trigger', trigger)

        success, message, data = self.get_table('admin')
        if success and len(data) == 0:
            self.new_record('admin', ('4237', 'Sir', 'Lance-A-Bot', '4237'))

        self.__delete_connection(cursor, db_conn)

    def __check_db_object(self, cursor: sqlite3.Cursor, type: str, name: str):
        """This method checks if the table/index/trigger exists and creates the object if it does not exist."""
        logger.debug(f'({type}, {name}) >> Started')

        # Check if the object is in the database files. Create the table if it does not exist.
        sql = f'SELECT name FROM sqlite_master WHERE type="{type}" AND name="{name}"'
        self.__sql_execute(cursor, sql)

        success, message, data = self.__sql_fetchall(cursor)
        if data:
            return

        logger.warning(f' >> {type} does not exist: {name} --> Creating the {type}.')

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

        if sql:
            self.__sql_execute(cursor, sql)

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
