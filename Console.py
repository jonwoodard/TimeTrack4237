import logging
import os
import csv
from datetime import datetime
from datetime import timedelta
from DatabaseManager import DatabaseManager

logger = logging.getLogger('TimeTrack.ConsoleUI')


class Console:
    """This class is the main interface."""

    def __init__(self, db_filename):
        self.__db_manager = DatabaseManager(db_filename)
        self.__db_manager._DatabaseManager__check_database()

    def import_student(self, csv_filename):
        """This method is used for testing purposes to import data from a csv file with students."""

        with open(csv_filename, 'r') as fh:
            csv_reader = csv.reader(fh)
            for record in csv_reader:
                self.__db_manager.new_record('student', tuple(record))

    def import_admin(self, csv_filename):
        """This method is used for testing purposes to import data from a csv file with admins."""

        with open(csv_filename, 'r') as fh:
            csv_reader = csv.reader(fh)
            for record in csv_reader:
                self.__db_manager.new_record('admin', tuple(record))

    def import_activity(self, csv_filename):
        """This method is used for testing purposes to import data from a csv file with activities."""

        with open(csv_filename, 'r') as fh:
            csv_reader = csv.reader(fh)
            for record in csv_reader:
                self.__db_manager.new_record('activity', tuple(record))

    def calculate_check_in_time(self, hrs, mins=0):
        """
        This method is used for testing purposes to determine the check in time for students.
        It calculates the check in time for a student who checked in a given number of hours and minutes ago.

        :param hrs:
        :param mins:
        :return:
        """

        current_time = datetime.now()
        pre_date = current_time - timedelta(hours=hrs, minutes=mins)
        return pre_date.isoformat(sep=' ', timespec='seconds')

    def sample_checkin(self):
        """This method is used for testing purposes to check in a few students."""

        self.__db_manager.checkin_student('0202', self.calculate_check_in_time(3))
        self.__db_manager.checkin_student('0404', self.calculate_check_in_time(2, 30))
        self.__db_manager.checkin_student('0505', self.calculate_check_in_time(2))
        self.__db_manager.checkin_student('0707', self.calculate_check_in_time(1, 30))
        self.__db_manager.checkin_student('1212', self.calculate_check_in_time(3))
        self.__db_manager.checkin_student('1414', self.calculate_check_in_time(2, 30))
        self.__db_manager.checkin_student('1515', self.calculate_check_in_time(2))
        self.__db_manager.checkin_student('1717', self.calculate_check_in_time(1, 30))

    def main_menu(self):
        """This method displays the main menu on the console."""
        user_data = tuple()

        while True:
            print('\nMAIN MENU')
            print('1. Scan Barcode')
            print('2. Display Checked In List')
            print('3. Admin Menu')
            print('8. Upload Google Sheet')
            print('9. Exit')
            choice = input('Choice? ')

            logger.debug(f' >> Main menu choice = {choice}')

            if choice == '1':
                barcode = input('Enter barcode: ')
                success, message, user_data = self.__db_manager.login_user(barcode)
                if user_data[0] == 'student':
                    self.student_menu(user_data)
                elif user_data[0] == 'admin':
                    pin = input('Enter pin: ')
                    success, message, valid_pin = self.__db_manager.check_pin(barcode, pin)
                    if valid_pin:
                        self.admin_menu(barcode)
                    else:
                        print(message)
                else:
                    print(message)

            elif choice == '2':
                _, _, data = self.__db_manager.get_checked_in_list()
                self.display_list(data, 'Barcode Name')

            elif choice == '3':
                self.admin_menu(user_data)

            elif choice == '8':
                self.__db_manager.upload_student_data_to_google_sheet()

            elif choice == '9':
                break

    def student_menu(self, user_data):
        """This method displays the student menu on the console."""
        barcode = user_data[2]

        while True:
            print('\nSTUDENT MENU')
            print('1. Check In')
            print('2. Check Out')
            print('3. Get Total Hours')
            print('4. Get Hours List')
            print('9. Exit')
            choice = input('Choice? ')

            logger.debug(f' >> Student menu choice = {choice}')

            if choice == '1':
                success, message, student_data = self.__db_manager.get_student_data(barcode)
                success, msg = self.__db_manager.checkin_student(barcode)
                print(student_data[0], ':  ', msg)

            elif choice == '2':
                success, message, student_data = self.__db_manager.get_student_data(barcode)
                success, msg = self.__db_manager.checkout_student(barcode)
                print(student_data[0], ':  ', msg)

            elif choice == '3':
                success, message, student_data = self.__db_manager.get_student_data(barcode)
                print(student_data[0], ':  Total Hours =', student_data[2])

            elif choice == '4':
                success, message, student_data = self.__db_manager.get_student_data(barcode)
                success, message, data = self.__db_manager.get_student_hours_table(barcode)
                print(student_data[0], ': ', student_data[1])
                self.display_table(data, ('Day', 'Date', 'Hours'))

            elif choice == '9':
                break

    def admin_menu(self, user_data):
        """This method displays the admin menu."""

        while True:
            print('\nADMIN MENU')
            print('1. Student Table Menu')
            print('2. Activity Table Menu')
            print('3. Admin Table Menu')
            print('4. Testing Data')
            print('9. Exit Admin Menu')
            choice = input('Choice? ')

            logger.debug(f' >> Admin menu choice = {choice}')

            if choice == '1':
                self.student_table_menu()

            elif choice == '2':
                self.activity_table_menu()

            elif choice == '3':
                self.admin_table_menu()

            elif choice == '4':
                self.testing_data_menu()

            elif choice == '9':
                break

    def student_table_menu(self):
        """This method displays the student table menu."""
        headers = ('rowid', 'Barcode', 'First Name', 'Last Name')

        while True:
            print('\nSTUDENT TABLE MENU')
            print('1. New Student')
            print('2. Edit a Student')
            print('3. Delete a Student')
            print('4. Import Students (CSV files)')
            print('9. Exit Student Table Menu')
            choice = input('Choice? ')

            if choice == '1':
                barcode = input('Enter barcode: ')
                first_name = input('Enter First name: ')
                last_name = input('Enter Last name : ')
                record = (barcode, first_name, last_name)
                self.__db_manager.new_record('student', record)

            elif choice == '2':
                _, _, student_table = self.__db_manager.get_table('student')
                self.display_table(student_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    barcode = input('Enter NEW barcode: ')
                    first_name = input('Enter New First name: ')
                    last_name = input('Enter New Last name : ')
                    record = (barcode, first_name, last_name)
                    self.__db_manager.edit_record('student', row_id, record)
                except:
                    pass

            elif choice == '3':
                _, _, student_table = self.__db_manager.get_table('student')
                self.display_table(student_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    response = input('Are you sure (y/n)? ')
                    if response == 'y':
                        self.__db_manager.delete_record('student', row_id)
                except:
                    pass

            elif choice == '4':
                print('CSV files format: barcode,first name,last name')
                csv_filename = input('CSV Filename? ')
                self.import_student(csv_filename)

            elif choice == '9':
                break

    def activity_table_menu(self):
        """This method displays the activity table menu."""

        headers = ('rowid', 'Barcode', 'Check In', 'Check Out')

        while True:
            print('\nACTIVITY TABLE MENU')
            print('1. New Activity')
            print('2. Edit an Activity')
            print('3. Delete an Activity')
            print('9. Exit Activity Table Menu')
            choice = input('Choice? ')

            if choice == '1':
                barcode = input('Enter barcode: ')
                date = input('Enter date (YYYY-MM-DD): ')
                in_time = input('Enter check in time  (HH:MM:SS): ')
                out_time = input('Enter check out time (HH:MM:SS): ')
                check_in = date + ' ' + in_time
                check_out = date + ' ' + out_time
                record = (barcode, check_in, check_out)
                self.__db_manager.new_record('activity', record)

            elif choice == '2':
                _, _, activity_table = self.__db_manager.get_table('activity')
                self.display_table(activity_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    _, _, data = self.__db_manager.get_record('activity', row_id)
                    if data:
                        barcode = data[1]
                        date = input('Enter date (YYYY-MM-DD): ')
                        in_time = input('Enter check in time  (HH:MM:SS): ')
                        out_time = input('Enter check out time (HH:MM:SS): ')
                        check_in = date + ' ' + in_time
                        check_out = date + ' ' + out_time
                        record = (barcode, check_in, check_out)
                        self.__db_manager.edit_record('activity', row_id, record)
                except:
                    pass

            elif choice == '3':
                _, _, activity_table = self.__db_manager.get_table('activity')
                self.display_table(activity_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    response = input('Are you sure (y/n)? ')
                    if response == 'y':
                        self.__db_manager.delete_record('activity', row_id)
                except:
                    pass

            elif choice == '9':
                break

    def admin_table_menu(self):
        """This method displays the admin table menu."""

        headers = ('rowid', 'Barcode', 'First Name', 'Last Name')
        while True:
            print('\nADMIN TABLE MENU')
            print('1. New Admin')
            print('2. Edit an Admin')
            print('3. Delete an Admin')
            print('4. Reset Admin PIN')
            print('9. Exit Admin Table Menu')
            choice = input('Choice? ')

            if choice == '1':
                barcode = input('Enter barcode: ')
                first_name = input('Enter First name: ')
                last_name = input('Enter Last name: ')
                pin = input('Enter a PIN: ')
                record = (barcode, first_name, last_name, pin)
                self.__db_manager.new_record('admin', record)

            elif choice == '2':
                _, _, admin_table = self.__db_manager.get_table('admin')
                self.display_table(admin_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    barcode = input('Enter NEW barcode: ')
                    first_name = input('Enter New First name: ')
                    last_name = input('Enter New Last name : ')
                    record = (barcode, first_name, last_name)
                    self.__db_manager.edit_record('admin', row_id, record)
                except:
                    pass

            elif choice == '3':
                _, _, admin_table = self.__db_manager.get_table('student')
                self.display_table(admin_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    response = input('Are you sure (y/n)? ')
                    if response == 'y':
                        self.__db_manager.delete_record('admin', row_id)
                except:
                    pass

            elif choice == '4':
                _, _, admin_table = self.__db_manager.get_table('admin')
                self.display_table(admin_table, headers)
                try:
                    row_id = int(input('Enter rowid: '))
                    old_pin = input('Enter the old PIN:')
                    new_pin = input('Enter the new PIN:' )
                    self.__db_manager.reset_pin(row_id, new_pin, old_pin)
                except:
                    pass

            elif choice == '9':
                break

    def testing_data_menu(self):
        """This method displays the testing data menu."""

        while True:
            print('\nTESTING DATA MENU')
            print('1. Import Students')
            print('2. Import Activities')
            print('3. Import Admins')
            print('4. Import ALL Sample Data')
            print('9. Exit Testing Data Menu')
            choice = input('Choice? ')

            if choice == '1':
                self.import_student('files/student.csv')

            elif choice == '2':
                self.import_activity('files/activity.csv')

            elif choice == '3':
                self.import_admin('files/admin.csv')

            elif choice == '4':
                self.import_student('files/student.csv')
                self.import_admin('files/admin.csv')
                self.import_activity('files/activity.csv')
                self.sample_checkin()

            elif choice == '9':
                break

    def display_table(self, table: list or tuple, headers: tuple=()):

        for header in headers:
            print(f'{header:<15}', end='')
        print()

        for record in table:
            for field in record:
                print(f'{field:<15}', end='')
            print()

    def display_list(self, lst: list or tuple, header: str = ''):

        print(f'{header:<25}')

        for field in lst:
            print(f'{field:<25}')
