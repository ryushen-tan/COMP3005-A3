# COMP 3005 - Assignment 3 Question 1

Ryushen Tan

I used Python and PostgreSQL to add, list, update and delete students.

## Setup

You need Python 3.10 or newer, PostgreSQL, `psql`, `createdb`, and pgAdmin 4.
Start PostgreSQL before running the app. Python does not need a compile step.

Run these commands from the repository folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

Set the connection details below. Change `postgres` to your database username
if needed. If your server needs a password, set `PGPASSWORD` on your computer.
Do not save the password in the code.

```sh
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
createdb students
export PGDATABASE=students
psql -v ON_ERROR_STOP=1 -d students -f sql/setup.sql
```

In PowerShell, use `$env:PGHOST = "localhost"` instead of `export PGHOST=localhost`.
Use the same format for the other variables.

`setup.sql` creates the table and adds John Doe, Jane Smith and Jim Beam.
Run it once in a new database. It stops with an error if the table already exists.

The app uses the `students` database and the connection details above.
You can also set the connection with `DATABASE_URL`:

```sh
export DATABASE_URL='dbname=students host=localhost port=5432 user=postgres'
```

## Run

```sh
python src/students.py list
python src/students.py add Alex Lee alex.lee@example.com 2023-09-03
python src/students.py update 4 alex.new@example.com
python src/students.py delete 4
```

The add command prints the new ID. Use that ID for update and delete. It will be
`4` for the first student added after setup. Leave out the date to store NULL.
Put names with spaces in quotes. Run `python src/students.py --help` for help.

| Command | Function | What it does |
|---|---|---|
| `list` | `getAllStudents()` | Shows all students, sorted by ID |
| `add` | `addStudent(first_name, last_name, email, enrollment_date)` | Adds a student and shows the new ID |
| `update` | `updateStudentEmail(student_id, new_email)` | Changes a student's email |
| `delete` | `deleteStudent(student_id)` | Deletes a student by ID |

I used SQL parameters to keep input separate from the query. PostgreSQL checks
the primary key, required fields and unique emails. Each function opens a
connection, runs its query and saves the change. If it fails, the change is undone.
The app shows an error if an email is already used or an ID is missing. It also
shows other database errors. Failed commands return an error code.

## Check in pgAdmin

Add your PostgreSQL server in pgAdmin with the same host, port and username.
Open the `students` database's Query Tool and run:

```sql
SELECT * FROM students ORDER BY student_id;
```

Run this again after each app command. You should see Alex appear after `add`,
the email change after `update`, and Alex disappear after `delete`.
Open `Schemas > public > Tables > students > Columns` and `Constraints` to
see the table's columns and rules. You can also run `setup.sql` in the Query Tool
in a new empty `students` database.

## Tests

The tests use PostgreSQL. Set the test connection and run:

```sh
export TEST_DATABASE_URL='dbname=students host=localhost port=5432 user=postgres'
python -m unittest discover -s tests -v
```

The database user needs permission to create schemas. Each test makes its own
schema and removes it when done. The app's student table stays the same.
The tests check the starting rows, all four functions, repeated emails, missing
IDs, NULL dates, SQL parameters, table rules and command errors.

## Video demonstration

Video link: not added yet.

Use [video_script.md](video_script.md) to record a video under five minutes.
Upload the video and add its link above before submitting.

## Files

- `src/students.py`: the app.
- `sql/setup.sql`: creates the table and adds the starting rows.
- `requirements.txt`: PostgreSQL driver.
- `tests/test_students.py`: tests for the app and database.
- `video_script.md`: what to show and say in the video.
