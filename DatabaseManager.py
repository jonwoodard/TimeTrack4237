import sqlite3
from sqlite3 import Error
import os
from datetime import datetime
import bcrypt
import logging

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

    def check_database(self):
        """This method creates the database and tables if they do not exist."""
        logger.debug('() >> Started')

        # Check if the database files exists.
        if not os.path.isfile(self.__filename):
            logger.warning(f' >> File does not exist: {self.__filename} --> Creating the database file.')

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Check if the tables and indexes are created.
        for table in self.__db_tables:
            self.__check_db_object(cursor, 'table', table)

        for index in self.__db_indexes:
            self.__check_db_object(cursor, 'index', index)

        for trigger in self.__db_triggers:
            self.__check_db_object(cursor, 'trigger', trigger)

        self.new_record('admin', ('4237', 'Sir Lance', 'A Bot', '4237'))

        self.delete_connection(cursor, db_conn)

    def create_connection(self):
        db_conn = None
        cursor = None
        try:
            # Connect to the database.
            db_conn = sqlite3.connect(self.__filename, isolation_level=None)
            try:
                cursor = db_conn.cursor()
            except Error:
                logger.exception(' >> Error with database cursor')
        except Error:
            logger.exception(' >> Error with database connection')

        return db_conn, cursor

    def delete_connection(self, cursor: sqlite3.Cursor, db_conn: sqlite3.Connection):
        cursor.close()
        db_conn.close()

    def sql_execute(self, cursor: sqlite3.Cursor, sql: str, parameters: tuple = None):
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

    def sql_fetch(self, cursor: sqlite3.Cursor, rows: str = 'all'):
        success = False
        message = ''
        data = list()
        try:
            if rows == 'all':
                data = cursor.fetchall()
            else:
                data = cursor.fetchone()
            success = True
        except Error as e:
            logger.exception(f'() >> Error with fetch.')
            success = False
            message = str(e)

        return success, message, data

    def table_in_database(self, table: str):
        result = table.lower() in self.__db_tables
        if not result:
            logger.debug(f' >> Invalid table: {table}')
        return result

    def get_table(self, table: str, filter: str = None):
        """This method returns a table of data, including the rowid.
        The table of data is returned as a list of n-tuples."""
        logger.debug(f'() >> Started')
        success = False
        message = ''
        data = list()
        table = table.lower()

        if not self.table_in_database(table):
            return False, 'Invalid table', data

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', data

        sql = ''
        parameters = None
        if table == 'student':
            sql = '''SELECT rowid, id, firstname, lastname FROM student ORDER BY id'''
        elif table == 'activity':
            if filter:
                sql = '''SELECT rowid, id, checkin, checkout FROM activity WHERE id=? ORDER BY checkin DESC'''
                parameters = (filter, )
            else:
                sql = '''SELECT rowid, id, checkin, checkout FROM activity ORDER BY checkin DESC'''
        elif table == 'admin':
            sql = '''SELECT rowid, id, firstname, lastname FROM admin ORDER BY id'''

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor)

        self.delete_connection(cursor, db_conn)

        return success, message, data

    def get_record(self, table: str, row_id: int):
        """This method returns a table of data, including the rowid.
        The table of data is returned as a list of n-tuples."""
        logger.debug(f'() >> Started')
        success = False
        message = ''
        data = list()
        table = table.lower()

        if not self.table_in_database(table):
            return False, 'Invalid table', data

        db_conn, cursor = self.create_connection()
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

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor)

        self.delete_connection(cursor, db_conn)

        return success, message, data

    def new_record(self, table: str, record: tuple):
        """This method adds a new record into a table."""
        logger.debug(f'() >> Started')
        success = False
        message = ''
        table = table.lower()

        if not self.table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        sql = ''
        if table == 'student':
            sql = 'INSERT INTO student (id, firstname, lastname) VALUES (?, ?, ?)'
        elif table == 'activity':
            sql = 'INSERT INTO activity (id, checkin, checkout) VALUES (?, ?, ?)'
        elif table == 'admin':
            pin = self.__encrypt_pin(record[3])
            record = record[0:3] + (pin, )
            sql = 'INSERT INTO admin (id, firstname, lastname, pin) VALUES (?, ?, ?, ?)'
        parameters = record

        success, message = self.sql_execute(cursor, sql, parameters)
        self.delete_connection(cursor, db_conn)

        return success, message

    def edit_record(self, table: str, row_id: int, record: tuple):
        """This method edits a record in a table."""
        logger.debug(f'() >> Started')
        success = False
        message = ''
        table = table.lower()

        if not self.table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.create_connection()
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

        success, message = self.sql_execute(cursor, sql, parameters)
        self.delete_connection(cursor, db_conn)

        return success, message

    def delete_record(self, table: str, row_id: int):
        """This method deletes a record from a table."""
        logger.debug(f'() >> started')
        success = False
        message = ''
        table = table.lower()

        if not self.table_in_database(table):
            return False, 'Invalid table'

        db_conn, cursor = self.create_connection()
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

        success, message = self.sql_execute(cursor, sql, parameters)
        self.delete_connection(cursor, db_conn)

        return success, message

    def check_barcode(self, barcode: str):
        """This method checks if a barcode is valid."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''
        barcode_type = 'Invalid'

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', False

        # Check if the student table contains a student with this barcode.
        sql = 'SELECT id, firstname, lastname FROM student WHERE id=?'
        parameters = (barcode,)

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor)
            if data:
                barcode_type = 'Student'

        if barcode_type == 'Invalid':
            # Check if the admin table contains an admin with this barcode.
            sql = 'SELECT id, firstname, lastname, pin FROM admin WHERE id=?'
            parameters = (barcode,)

            success, message = self.sql_execute(cursor, sql, parameters)
            if success:
                success, message, data = self.sql_fetch(cursor)
                if data:
                    barcode_type = 'Admin'

        self.delete_connection(cursor, db_conn)

        return success, message, barcode_type

    def check_pin(self, barcode: str, pin: str):
        """This method checks if a pin is valid."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''
        valid = False

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', False

        # Check if the admin table contains an admin with this barcode.
        sql = 'SELECT pin FROM admin WHERE id=?'
        parameters = (barcode,)

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor, 'one')
            if data and self.__is_pin_correct(pin, data[0]):
                valid = True

        self.delete_connection(cursor, db_conn)

        return success, message, valid

    def reset_pin(self, row_id: int, new_pin: str, old_pin: str):
        """This method checks if a pin is valid."""
        logger.debug(f'() >> Started')
        success = False
        message = ''
        valid = False

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Check if the admin table contains an admin with this barcode.
        sql = 'SELECT pin FROM admin WHERE rowid=?'
        parameters = (row_id, )

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor, 'one')
            if data:
                if self.__is_pin_correct(old_pin, data[0]):
                    sql = 'UPDATE admin SET pin=? WHERE rowid=?'
                    parameters = (self.__encrypt_pin(new_pin), row_id)

                    success, message = self.sql_execute(cursor, sql, parameters)
                else:
                    success = False
                    message = 'Incorrect PIN.'

        self.delete_connection(cursor, db_conn)

        return success, message

    def __is_pin_correct(self, pin: str, encrypted_pin: str):
        return bcrypt.checkpw(str(pin).encode(), str(encrypted_pin).encode())

    def __encrypt_pin(self, pin: str):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pin.encode(), salt)

        return hashed.decode()

    def checkin_student(self, barcode: str, checkin: str = 'NOW'):
        """This method will check in a student. The student must not be checked in already."""
        logger.debug(f'({barcode}, {checkin}) >> Started')

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

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error'

        # Add the student to the activity table.
        if checkout == 'NOW':
            checkout = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = '''UPDATE activity SET checkout=?
                WHERE id=? AND checkout IS NULL'''
        parameters = (checkout, barcode)

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, total_hours = self.__total_hours(cursor, barcode)
            message = f'Checked out. Total hours: {total_hours:.2f}'
        else:
            success, message, total_hours = self.__total_hours(cursor, barcode)
            message = f'NOT Checked out. Total hours: {total_hours:.2f}'

        self.delete_connection(cursor, db_conn)

        return success, message

    def get_student_data(self, barcode: str):
        """This method returns a student name given a barcode."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''

        name = ''
        status = ''
        total_hours = 0.0

        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', ()

        # Get the student name of the student.
        sql = 'SELECT firstname || " " || lastname FROM student WHERE id=?'
        parameters = (barcode,)
        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor, 'one')
            if success:
                name = data[0]

        # Get the status of the student ('Checked In' or 'Checked Out').
        sql = '''SELECT rowid, id, checkin, checkout FROM activity 
                WHERE id=? AND checkout IS NULL'''
        parameters = (barcode, )
        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor, 'one')
            if data:
                status = 'Checked In'
            else:
                status = 'Checked Out'

        # Get the total hours worked.
        success, message, total_hours = self.__total_hours(cursor, barcode)

        self.delete_connection(cursor, db_conn)

        return success, message, (name, status, total_hours)

    def get_total_hours(self, barcode: str):
        """This method returns the total hours for a student."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''

        total_hours = 0.0
        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', total_hours

        success, message, total_hours = self.__total_hours(cursor, barcode)

        self.delete_connection(cursor, db_conn)

        return success, message, total_hours

    def get_student_hours_table(self, barcode: str):
        """This method returns a list of the hours for a student, totaled for each day."""
        logger.debug(f'({barcode}) >> Started')
        success = False
        message = ''

        hours_table = list()
        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', hours_table

        sql = '''SELECT DATE(checkin),
                ROUND(SUM(JULIANDAY(checkout) - JULIANDAY(checkin)) * 24.0, 2)
                FROM activity WHERE id=? AND checkout IS NOT NULL
                GROUP BY DATE(checkin) ORDER BY DATE(checkin) DESC'''
        parameters = (barcode, )

        success, message = self.sql_execute(cursor, sql, parameters)
        if success:
            success, message, data = self.sql_fetch(cursor)

            # This will create the table of hours, which is a list of 3-tuples
            # [ ('day of week', 'date', 'hours'), ... ]
            hours_table = list()
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for (date, hours) in data:
                # Convert the date string to a datetime object to determine the day of the week.
                day_of_week = days[datetime.strptime(date, '%Y-%m-%d').weekday()]
                hours_table.append((day_of_week, date, f'{hours:5.2f}'))

        self.delete_connection(cursor, db_conn)

        return success, message, hours_table

    def get_checked_in_list(self):
        """This method returns a list of students currently checked in."""
        logger.debug('() >> Started')
        success = False
        message = ''

        lst = list()
        db_conn, cursor = self.create_connection()
        if not db_conn or not cursor:
            return False, 'Database connection error or cursor error', lst

        sql = '''SELECT "(" || student.id || ")  " || student.lastname || ", " || student.firstname
                FROM student JOIN activity ON student.id=activity.id
                WHERE activity.checkout IS NULL
                ORDER BY student.lastname ASC, student.firstname ASC'''

        success, message = self.sql_execute(cursor, sql)
        if success:
            # data is a list of 1-tuples: [('name (id)', ), ....
            success, message, data = self.sql_fetch(cursor)
            if success:
                # Convert data into a list of strings
                for item in data:
                    lst.append(item[0])

        self.delete_connection(cursor, db_conn)

        return success, message, lst

    def __total_hours(self, cursor: sqlite3.Cursor, barcode: str):
        total_hours = 0.0

        # Sum the total hours logged from previous checkins and checkouts.
        sql = '''SELECT SUM(JULIANDAY(checkout) - JULIANDAY(checkin)) * 24.0
                FROM activity WHERE id=? AND checkout IS NOT NULL'''
        parameters = (barcode, )

        success, message = self.sql_execute(cursor, sql, parameters)
        if not success:
            return success, message, 0.0

        success, message, data = self.sql_fetch(cursor, 'one')
        if not success:
            return success, message, 0.0

        if data and data[0]:
            total_hours = round(float(data[0]), 2)

        return success, message, total_hours

    def __check_db_object(self, cursor: sqlite3.Cursor, type: str, name: str):
        """This method checks if the table exists and creates the table if it does not exist."""
        logger.debug(f'({type}, {name}) >> Started')

        # Check if the student table is in the database files. Create the table if it does not exist.
        sql = f'SELECT name FROM sqlite_master WHERE type="{type}" AND name="{name}"'
        self.sql_execute(cursor, sql)

        success, message, data = self.sql_fetch(cursor)
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
            self.sql_execute(cursor, sql)

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
