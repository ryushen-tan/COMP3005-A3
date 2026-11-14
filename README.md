COMP 3005 Assignment 3 Question 1

Ryushen Tan
Student number 101269064

I used Python and PostgreSQL to add show update and delete students

Setup

You need Python PostgreSQL and pgAdmin
These steps are for Mac or Linux
Start PostgreSQL and open a terminal in the repository folder

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Connect to the database

Change postgres to your database username
Change the host or port if your server uses different settings

```sh
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGDATABASE=students
```

If your server needs a password run this and replace yourpassword

```sh
export PGPASSWORD='yourpassword'
```

Create the database and starting students
Only run these two commands once

```sh
createdb students
psql -v ON_ERROR_STOP=1 -f sql/setup.sql
```

Run the app

Show all students

```sh
python src/students.py list
```

Add a student

```sh
python src/students.py add Alex Lee alex.lee@example.com 2023-09-03
```

The app prints the new student ID
Use that ID instead of 4 below if it is different

Change the email

```sh
python src/students.py update 4 alex.new@example.com
```

Delete the student

```sh
python src/students.py delete 4
```

Check in pgAdmin

Connect using the same host port and username
Open the students database and its Query Tool
Run this after each change to see the results

```sql
SELECT * FROM students ORDER BY student_id;
```

Video

https://youtu.be/YXlqf66yitk
