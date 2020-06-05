import json
import os
import psycopg2
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from psycopg2.extras import RealDictCursor
from functions import create_drop_db, all_functions


def root_connection():
    connection_ = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="changeme",
        host="192.168.1.54",
        port="5432"
            )
    return connection_


def user_connection(name):
    connection_ = psycopg2.connect(
        database=name,
        user="polina",
        password="changeme",
        host="192.168.1.54",
        port="5432"
    )
    return connection_


def center(toplevel_):
    toplevel_.update_idletasks()
    screen_width = toplevel_.winfo_screenwidth()
    screen_height = toplevel_.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel_.geometry().split('+')[0].split('x'))
    x = screen_width / 2 - size[0] / 2
    y = screen_height / 2 - size[1] / 2
    toplevel_.geometry("+%d+%d" % (x, y))


def display_data(title, data):
    print_entries = ''
    print_entries += title + ":\n"
    for entry in data:
        for key in entry:
            print_entries += key + ': ' + str(entry[key]) + '\n'

        print_entries += '\n'

    return print_entries


def display_all(connection_):
    display = Toplevel()
    center(display)
    display.resizable(False, False)
    display.title('View all entries')

    cursor_ = connection_.cursor(cursor_factory=RealDictCursor)

    print_entries = ""

    cursor_.execute("select get_all_doctors();")
    results = json.loads(json.dumps((cursor_.fetchall())))
    if results[0]['get_all_doctors']:
        print_entries += display_data("Doctors", results[0]['get_all_doctors'])

    cursor_.execute("select get_all_patients();")
    results = json.loads(json.dumps((cursor_.fetchall())))
    if results[0]['get_all_patients']:
        print_entries += display_data("Patients", results[0]['get_all_patients'])

    if print_entries == "":
        print_entries = "Currently all tables are empty."

    show_entries_result = Label(display, text=print_entries)
    show_entries_result.grid(row=0, column=0, columnspan=2)


def add_new_patient(connection_):
    def add_entry():
        patient_name = name_.get()
        birthday_ = birthday.get()
        phone_number_ = phone_number.get().replace('+7', '8')
        doctor_ = doctor.get()

        if patient_name == '' or birthday_ == '' or phone_number_ == '' or doctor_ == '':
            error.configure(text="Please fill out all fields!")
        elif not check_name(patient_name):
            error.configure(text="The first name and a last name and can only contain letters!")
        elif not check_birthday(birthday_):
            error.configure(text="Invalid birthday!")
        elif not check_phone_number(phone_number_):
            error.configure(text="Incorrect data format, should be +7XXXXXXXXXX or 8XXXXXXXXXX")
        elif not all(c.isnumeric() for c in doctor_):
            error.configure(text="Doctor ID must be a number")
        else:
            cursor_ = connection_.cursor()

            try:
                cursor_.execute(f"select add_patient('{patient_name}','{birthday_}','{phone_number_}', '{doctor_}');")
                cursor_.close()
                name_.delete(0, 'end')
                birthday.delete(0, 'end')
                phone_number.delete(0, 'end')
                doctor.delete(0, 'end')
                error.configure(text="")
                success.configure(text="Patient added to the DB!")
            except:
                error.configure(text="A doctor with this ID doesn't exist in the database")

    new_entry = Toplevel()
    center(new_entry)
    new_entry.resizable(False, False)
    new_entry.title('Add a new entry')

    name_ = Entry(new_entry, width=30)
    name_.grid(row=0, column=1, padx=20)
    birthday = Entry(new_entry, width=30)
    birthday.grid(row=1, column=1, padx=20)
    phone_number = Entry(new_entry, width=30)
    phone_number.grid(row=2, column=1, padx=20)
    doctor = Entry(new_entry, width=30)
    doctor.grid(row=3, column=1, padx=20)

    name_label = Label(new_entry, text="Patient name")
    name_label.grid(row=0, column=0)
    birthday_label = Label(new_entry, text="Birthday (dd-mm-yyyy)")
    birthday_label.grid(row=1, column=0)
    phone_number_label = Label(new_entry, text="Phone number")
    phone_number_label.grid(row=2, column=0)
    doctor_label = Label(new_entry, text="Doctor ID")
    doctor_label.grid(row=3, column=0)

    error = Label(new_entry, text="", fg="red")
    error.grid(row=4, column=0, columnspan=2)

    success = Label(new_entry, text="")
    success.grid(row=5, column=0, columnspan=2)

    submit_entry_button = Button(new_entry, text="Add entry", padx=50, pady=10, command=add_entry)
    submit_entry_button.grid(row=6, column=0, columnspan=2)


def add_new_doctor(connection_):
    def add_entry():
        doctor_name = name_.get()

        if doctor_name == '':
            error.configure(text="Please fill out all fields!")
        elif not check_name(doctor_name):
            error.configure(text="The first name and a last name and can only contain letters!")
        else:
            cursor_ = connection_.cursor()

            try:
                cursor_.execute(f"select add_doctor('{doctor_name}');")
                cursor_.close()
                name_.delete(0, 'end')
                error.configure(text="")
                success.configure(text="Doctor added to the DB!")
            except psycopg2.Error as e:
                error.configure(text=e)

    new_entry = Toplevel()
    center(new_entry)
    new_entry.resizable(False, False)
    new_entry.title('Add a new entry')

    name_ = Entry(new_entry, width=30)
    name_.grid(row=0, column=1, padx=20)

    name_label = Label(new_entry, text="Doctor name")
    name_label.grid(row=0, column=0)

    error = Label(new_entry, text="", fg="red")
    error.grid(row=1, column=0, columnspan=2)

    success = Label(new_entry, text="")
    success.grid(row=2, column=0, columnspan=2)

    submit_entry_button = Button(new_entry, text="Add entry", padx=50, pady=10, command=add_entry)
    submit_entry_button.grid(row=3, column=0, columnspan=2)


def edit_patients(connection_, id_):
    def edit():
        value = search_value.get()

        if choice.get() == 1:
            if not check_name(value):
                error.configure(text="The first name and a last name and can only contain letters!")
            else:
                edit_patient('name', value)
        elif choice.get() == 2:
            if not check_birthday(value):
                error.configure(text="Invalid birthday!")
            else:
                edit_patient('birthday', value)
        elif choice.get() == 3:
            if not check_phone_number(value):
                error.configure(text="Incorrect data format, should be +7XXXXXXXXXX or 8XXXXXXXXXX")
            else:
                edit_patient('phone_number', value.replace('+7', '8'))
        elif choice.get() == 4:
            if not check_name(value):
                error.configure(text="Doctor ID must be a number")
            else:
                edit_patient('doctor', int(value))

    def edit_patient(field, value):
        cursor_ = connection_.cursor()
        cursor_.execute(f"select check_patient('{id_}');")
        result = cursor_.fetchall()
        if result != [(None,)]:
            try:
                cursor_.execute(f"select edit_patient_{field}('{id_}', '{value}');")
                success.configure(text="Patient entry has been edited!")

            except psycopg2.Error as e:
                messagebox.showerror("error", e)

        cursor_.close()

    edit_window = Toplevel()
    center(edit_window)
    edit_window.resizable(False, False)
    edit_window.title('Edit')
    choice = IntVar()
    choice.set('1')
    Label(edit_window, text="Edit:").pack()
    Radiobutton(edit_window, text="Name", variable=choice, value=1).pack()
    Radiobutton(edit_window, text="Birthday (dd-mm-yyyy)", variable=choice, value=2).pack()
    Radiobutton(edit_window, text="Phone number", variable=choice, value=3).pack()
    Radiobutton(edit_window, text="Doctor ID", variable=choice, value=4).pack()
    Label(edit_window, text="").pack()
    Label(edit_window, text="Value:").pack()
    search_value = Entry(edit_window, width=30)
    search_value.pack()
    Label(edit_window, text="").pack()
    error = Label(edit_window, text="", fg="red")
    error.pack()
    success = Label(edit_window, text="")
    success.pack()
    edit_button = Button(edit_window, text="Apply changes", padx=50, pady=10, command=edit)
    edit_button.pack()


def edit_doctors(connection_, id_):
    def edit():
        value = search_value.get()

        if not check_name(value):
            error.configure(text="The first name and a last name and can only contain letters!")
        elif value.isdigit():
            edit_doctor(value)
        else:
            error.configure(text="The ID must be a number!")

    def edit_doctor(value):
        cursor_ = connection_.cursor()
        cursor_.execute(f"select check_doctor('{id_}');")
        result = cursor_.fetchall()
        if result != [(None,)]:
            try:
                cursor_.execute(f"select edit_doctor_name('{id_}', '{value}');")
                success.configure(text="Doctor entry has been edited!")

            except psycopg2.Error as e:
                messagebox.showerror("error", e)

        cursor_.close()

    edit_window = Toplevel()
    center(edit_window)
    edit_window.resizable(False, False)
    edit_window.title('Edit')
    Label(edit_window, text="Name:").pack()
    search_value = Entry(edit_window, width=30)
    search_value.pack()
    Label(edit_window, text="").pack()
    error = Label(edit_window, text="", fg="red")
    error.pack()
    success = Label(edit_window, text="")
    success.pack()
    edit_button = Button(edit_window, text="Apply changes", padx=50, pady=10, command=edit)
    edit_button.pack()


def delete_database(connection_, window):
    name_ = connection_.get_dsn_parameters()['dbname']
    connection_.close()
    root_con = root_connection()
    cursor_ = root_con.cursor()
    try:
        cursor_.execute(create_drop_db)
        cursor_.execute(f"select delete_database('{name_}');")
        cursor_.close()
        root_con.close()

        for button in root.pack_slaves():
            if button['text'] == name_:
                button.destroy()

        databases.remove(name_)
        update_databases()
        window.destroy()

    except psycopg2.OperationalError as error:
        messagebox.showerror("error", error)


def find_entry_patients(connection_, option):
    def clicked():
        if search_value.get():
            error.configure(text="")
            value = search_value.get()

            if option == 'find':
                if choice.get() == 1:
                    if check_name(value):
                        find_patients('name', value)
                    else:
                        error.configure(text="The first name and a last name and can only contain letters!")
                elif choice.get() == 2:
                    if check_birthday(value):
                        find_patients('birthday', value)
                    else:
                        error.configure(text="Invalid birthday!")
                elif choice.get() == 3:
                    if check_phone_number(value):
                        find_patients('phone_number', value.replace('+7', '8'))
                    else:
                        error.configure(text="Incorrect data format, should be +7XXXXXXXXXX or 8XXXXXXXXXX")
                elif choice.get() == 4:
                    if value.isdigit():
                        find_patients('doctor', int(value))
                    else:
                        error.configure(text="Doctor ID must be a number")

            elif option == 'edit':
                fail = 0
                if choice.get() == 1:
                    if check_name(value):
                        find_patients('name', value)
                    else:
                        error.configure(text="The first name and a last name and can only contain letters!")
                        fail = 1
                elif choice.get() == 2:
                    if check_birthday(value):
                        find_patients('birthday', value)
                    else:
                        error.configure(text="Invalid birthday!")
                        fail = 1
                elif choice.get() == 3:
                    if check_phone_number(value):
                        find_patients('phone_number', value.replace('+7', '8'))
                    else:
                        error.configure(text="Incorrect data format, should be +7XXXXXXXXXX or 8XXXXXXXXXX")
                        fail = 1
                elif choice.get() == 4:
                    if value.isdigit():
                        find_patients('doctor', int(value))
                    else:
                        error.configure(text="Doctor ID must be a number")
                        fail = 1

                if fail == 0:
                    Label(search, text="").pack()
                    Label(search, text="\nPlease specify the ID of the patient\n you'd like to edit:").pack()
                    edit_index = Entry(search, width=30)
                    edit_index.pack()
                    Button(search, text="Edit entry", command=lambda: edit_patients(connection_, edit_index.get()),
                           width=20).pack()

            search_value.delete(0, 'end')

        else:
            error.configure(text="Please enter a value to search for")

    def find_patients(field, value):
        display = Toplevel()
        center(display)
        display.resizable(False, False)
        display.title('View all entries')

        print_entries = ""

        cursor_ = connection_.cursor(cursor_factory=RealDictCursor)

        try:
            cursor_.execute(f"select get_patients_by_{field}('{value}');")
            results = json.loads(json.dumps((cursor_.fetchall())))

            if results[0][f"get_patients_by_{field}"]:
                print_entries += display_data("Patients", results[0][f"get_patients_by_{field}"])

        except psycopg2.Error as error:
            messagebox.showerror("error", error)

        cursor_.close()

        if print_entries == "":
            print_entries = "No patients were found."

        show_entries_result = Label(display, text=print_entries)
        show_entries_result.grid(row=0, column=0, columnspan=2)

    search = Toplevel()
    center(search)
    search.resizable(False, False)
    search.title('Search')
    choice = IntVar()
    choice.set('1')
    Label(search, text="Search by:").pack()
    Radiobutton(search, text="Name", variable=choice, value=1).pack()
    Radiobutton(search, text="Birthday (dd-mm-yyyy)", variable=choice, value=2).pack()
    Radiobutton(search, text="Phone number", variable=choice, value=3).pack()
    Radiobutton(search, text="Doctor ID", variable=choice, value=4).pack()
    Label(search, text="").pack()
    Label(search, text="Value:").pack()
    search_value = Entry(search, width=30)
    search_value.pack()
    Label(search, text="").pack()
    error = Label(search, text="", fg="red")
    error.pack()
    Button(search, text="Find", command=lambda: clicked(), width=20).pack()


def find_entry_doctors(connection_, option):
    def clicked():
        if search_value.get():
            error.configure(text="")
            value = search_value.get()
            fail = 0

            if option == 'find':
                if check_name(value):
                    find_doctors(value)
                else:
                    error.configure(text="The first name and a last name and can only contain letters!")

            elif option == 'edit':
                if check_name(value):
                    find_doctors(value)
                else:
                    error.configure(text="The first name and a last name and can only contain letters!")
                    fail = 1

                if fail == 0:
                    Label(search, text="").pack()
                    Label(search, text="\nPlease specify the ID of the doctor\n you'd like to edit:").pack()
                    edit_index = Entry(search, width=30)
                    edit_index.pack()
                    Button(search, text="Edit entry", command=lambda: edit_doctors(connection_, edit_index.get()),
                           width=20).pack()

            search_value.delete(0, 'end')

        else:
            error.configure(text="Please enter a value to search for")

    def find_doctors(value):
        display = Toplevel()
        center(display)
        display.resizable(False, False)
        display.title('View all entries')

        print_entries = ""

        cursor_ = connection_.cursor(cursor_factory=RealDictCursor)

        try:
            cursor_.execute(f"select get_doctors_by_name('{value}');")
            results = json.loads(json.dumps((cursor_.fetchall())))

            if results[0][f"get_doctors_by_name"]:
                print_entries += display_data("Doctors", results[0][f"get_doctors_by_name"])

        except psycopg2.Error as e:
            messagebox.showerror("error", e)

        cursor_.close()

        if print_entries == "":
            print_entries = "No doctors were found."

        show_entries_result = Label(display, text=print_entries)
        show_entries_result.grid(row=0, column=0, columnspan=2)

    search = Toplevel()
    center(search)
    search.resizable(False, False)
    search.title('Search')
    Label(search, text="Name:").pack()
    search_value = Entry(search, width=30)
    search_value.pack()
    Label(search, text="").pack()
    error = Label(search, text="", fg="red")
    error.pack()
    Button(search, text="Find", command=lambda: clicked(), width=20).pack()


def delete_entry_patients(connection_):
    def delete_():
        value = search_value.get()

        if choice.get() == 1:
            if value.isdigit():
                delete_patient('ID', value)
            else:
                error.configure(text="The ID must be a number")
        elif choice.get() == 2:
            if check_name(value):
                delete_patient('name', value)
            else:
                error.configure(text="The first name and a last name and can only contain letters!")
        elif choice.get() == 3:
            if check_birthday(value):
                delete_patient('birthday', value)
            else:
                error.configure(text="Invalid birthday!")
        elif choice.get() == 4:
            if check_phone_number(value):
                delete_patient('phone_number', value.replace('+7', '8'))
            else:
                error.configure(text="Incorrect data format, should be +7XXXXXXXXXX or 8XXXXXXXXXX")
        elif choice.get() == 5:
            if value.isdigit():
                delete_patient('doctor', int(value))
            else:
                error.configure(text="Doctor ID must be a number")

    def delete_patient(field, value):
        cursor_ = connection_.cursor()

        if field == 'ID':
            cursor_.execute(f"select check_patient('{value}');")
            result = cursor_.fetchall()

            if result != [(None,)]:
                try:
                    cursor_.execute(f"select delete_patient_by_{field}('{value}');")
                    success.configure(text="Patient entry has been deleted!")

                except psycopg2.Error:
                    messagebox.showerror("error", "A patient with this ID does not exist")

        else:
            try:
                cursor_.execute(f"select delete_patient_by_{field}('{value}');")
                success.configure(text="Patient entries have been deleted!")

            except psycopg2.Error as e:
                messagebox.showerror("error", e)

        cursor_.close()

    delete_window = Toplevel()
    center(delete_window)
    delete_window.resizable(False, False)
    delete_window.title('Delete')
    choice = IntVar()
    choice.set('1')
    Label(delete_window, text="Delete by:").pack()
    Radiobutton(delete_window, text="ID", variable=choice, value=1).pack()
    Radiobutton(delete_window, text="Name", variable=choice, value=2).pack()
    Radiobutton(delete_window, text="Birthday (dd-mm-yyyy)", variable=choice, value=3).pack()
    Radiobutton(delete_window, text="Phone number", variable=choice, value=4).pack()
    Radiobutton(delete_window, text="Doctor ID", variable=choice, value=5).pack()
    Label(delete_window, text="").pack()
    Label(delete_window, text="Value:").pack()
    search_value = Entry(delete_window, width=30)
    search_value.pack()
    Label(delete_window, text="").pack()
    error = Label(delete_window, text="", fg="red")
    error.pack()
    success = Label(delete_window, text="")
    success.pack()
    edit_button = Button(delete_window, text="Delete", padx=50, pady=10, command=delete_)
    edit_button.pack()


def delete_entry_doctors(connection_):
    def delete_():
        value = search_value.get()

        if choice.get() == 1:
            if value.isdigit():
                delete_doctor('ID', value)
            else:
                error.configure(text="The ID must be a number")
        elif choice.get() == 2:
            if check_name(value):
                delete_doctor('name', value)
            else:
                error.configure(text="The first name and a last name and can only contain letters!")

    def delete_doctor(field, value):
        cursor_ = connection_.cursor()

        if field == 'ID':
            cursor_.execute(f"select check_doctor('{value}');")
            result = cursor_.fetchall()

            if result != [(None,)]:
                try:
                    cursor_.execute(f"select delete_doctor_by_{field}('{value}');")
                    success.configure(text="Doctor entry has been deleted!")

                except psycopg2.Error:
                    messagebox.showerror("error", "A doctor with this ID does not exist")

        else:
            try:
                cursor_.execute(f"select delete_doctor_by_{field}('{value}');")
                success.configure(text="Doctor entries have been deleted!")

            except psycopg2.Error as e:
                messagebox.showerror("error", e)

        cursor_.close()

    delete_window = Toplevel()
    center(delete_window)
    delete_window.resizable(False, False)
    delete_window.title('Delete')
    choice = IntVar()
    choice.set('1')
    Label(delete_window, text="Delete by:").pack()
    Radiobutton(delete_window, text="ID", variable=choice, value=1).pack()
    Radiobutton(delete_window, text="Name", variable=choice, value=2).pack()
    Label(delete_window, text="").pack()
    Label(delete_window, text="Value:").pack()
    search_value = Entry(delete_window, width=30)
    search_value.pack()
    Label(delete_window, text="").pack()
    error = Label(delete_window, text="", fg="red")
    error.pack()
    success = Label(delete_window, text="")
    success.pack()
    edit_button = Button(delete_window, text="Delete", padx=50, pady=10, command=delete_)
    edit_button.pack()


def clear_tables(connection_):
    clear = Toplevel()
    center(clear)
    clear.resizable(False, False)
    clear.title('Clear tables')
    Button(clear, text="Clear Patients", command=lambda: clear_data(connection_, 'patients'), width=50).pack()
    Button(clear, text="Clear All", command=lambda: clear_data(connection_, 'all'), width=50).pack()


def clear_data(connection_, type_):
    cursor_ = connection_.cursor()

    if type_ == 'patients':
        cursor_.execute("select clear_patients();")
    else:
        cursor_.execute("select clear_doctors();")

    cursor_.close()


def open_db(connection_):
    db = Toplevel()
    center(db)
    db.resizable(False, False)
    db.title('Database')
    Button(db, text="Add a new patient", command=lambda: add_new_patient(connection_), width=50).pack()
    Button(db, text="Add a new doctor", command=lambda: add_new_doctor(connection_), width=50).pack()
    Button(db, text="Find a patient", command=lambda: find_entry_patients(connection_, 'find'), width=50).pack()
    Button(db, text="Find a doctor", command=lambda: find_entry_doctors(connection_, 'find'), width=50).pack()
    Button(db, text="Edit entry of a patient", command=lambda: find_entry_patients(connection_, 'edit'),
           width=50).pack()
    Button(db, text="Edit entry of a doctor", command=lambda: find_entry_doctors(connection_, 'edit'), width=50).pack()
    Button(db, text="Delete entry of a patient", command=lambda: delete_entry_patients(connection_),
           width=50).pack()
    Button(db, text="Delete entry of a doctor", command=lambda: delete_entry_doctors(connection_),
           width=50).pack()
    Button(db, text="View all entries", command=lambda: display_all(connection_), width=50).pack()
    Button(db, text="Clear tables", command=lambda: clear_tables(connection_), width=50).pack()
    Button(db, text="Delete DB", command=lambda: delete_database(connection_, db), width=50, bg="#ca3433").pack()


def create_db(name_):
    try:  # if no errors -> DB exists, else -> create DB
        user_connection(name_)
        messagebox.showerror("error", "A database with this name already exists. Please choose a different name.")
    except psycopg2.OperationalError:
        connection_ = root_connection()  # master connection is necessary to initially create a database with
        # non-root owner
        connection_.autocommit = True
        cursor_ = connection_.cursor()

        try:
            cursor_.execute(create_drop_db)
            cursor_.execute(f"select create_database('{name_}');")
            cursor_.close()
        except psycopg2.OperationalError:
            messagebox.showerror("error", "Failed to create a new database")
            cursor_.close()
            connection_.close()

        try:
            connection_ = user_connection(name_)
            cursor_ = connection_.cursor()
            cursor_.execute(all_functions)  # creating tables architecture
            cursor_.close()
            databases.append(name_)
            update_databases()
            Button(root, text=name_, command=lambda: open_db(connection_), width=50).pack()
        except psycopg2.OperationalError as error:
            messagebox.showerror("error", error)
            cursor_.close()
            connection_.close()


def update_databases():
    with open('databases.txt', 'w') as file:
        for name_ in databases:
            file.write("%s\n" % name_)


def create_new_db():
    new_db = Toplevel()
    center(new_db)
    new_db.resizable(False, False)
    new_db.title('Add a new DB')
    db_name = Entry(new_db, width=30)
    db_name.grid(row=1, column=1, padx=20)
    db_name_label = Label(new_db, text="DB name")
    db_name_label.grid(row=1, column=0)

    Label(new_db, text="").grid(row=2, column=0)

    submit_entry_button = Button(new_db, text="Create DB", padx=50, pady=10, command=lambda: create_db(db_name.get()))
    submit_entry_button.grid(row=3, column=0, columnspan=2)


def check_name(name_):
    if len(name_.split()) != 2:
        return False
    first_name = name_.split()[0]
    last_name = name_.split()[1]
    if (not all(c.isalpha() for c in first_name)) or (not all(c.isalpha() for c in last_name)):
        return False
    else:
        return True


def check_birthday(birthday):
    try:
        datetime.strptime(birthday, '%d-%m-%Y')
        return True
    except:
        return False


def check_phone_number(number):
    number = number.replace('+7', '8')

    if len(number) != 11:
        return False
    else:
        return True


if __name__ == "__main__":
    root = Tk()
    center(root)
    root.resizable(False, False)

    Button(root, text="Create a new DB", command=create_new_db, width=50, bg="#99edc3").pack()

    if not os.path.exists('databases.txt'):
        with open('databases.txt', 'w+'):
            pass
        databases = []
    else:
        with open('databases.txt', "r") as fid:

            if not os.stat('databases.txt').st_size == 0:
                content = fid.readlines()
                databases = [x.strip() for x in content]

            else:
                databases = []

    for name in databases:
        connection = user_connection(name)
        cursor = connection.cursor()
        cursor.execute(all_functions)  # creating tables architecture
        cursor.close()
        Button(root, text=name, command=lambda: open_db(connection), width=50).pack()

    root.mainloop()
