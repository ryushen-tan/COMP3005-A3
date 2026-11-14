# A3 Question 1 video script (about 4 minutes)

Before recording, follow the README to set up Python and the database connection.
Open a terminal in the `q1` folder and pgAdmin beside it.
Use a new empty `students` database to show the setup.
Keep connection passwords out of the recording.

## 1. Introduction and setup (60 seconds)

"Hi, I'm Ryushen. This is Assignment 3 Question 1 for COMP 3005.
I used Python and PostgreSQL to add, show, update and delete students."

Show `sql/setup.sql`. In pgAdmin's Query Tool, connected to the empty `students`
database, open and run that file. Do not rerun it if the table already exists.

"The student ID is the primary key. PostgreSQL gives each new student an ID.
First name, last name and email cannot be NULL. Two students cannot use the same
email. Enrollment date stores a date and can be NULL. These are the three
students from the assignment."

Run in pgAdmin:

```sql
SELECT * FROM students ORDER BY student_id;
```

## 2. List the students (30 seconds)

```sh
python src/students.py list
```

"This calls getAllStudents. It shows all five columns for every
student, ordered by student ID. The three rows match pgAdmin."

## 3. Add a student (40 seconds)

```sh
python src/students.py add Alex Lee alex.lee@example.com 2023-09-03
```

"This calls addStudent. PostgreSQL gives the student an ID and saves the new
row. The ID is shown here."

Rerun the SELECT in pgAdmin and point to Alex's row. Check the new
ID; use it instead of `4` below if different.

## 4. Update the email (35 seconds)

```sh
python src/students.py update 4 alex.new@example.com
```

"This calls updateStudentEmail with Alex's ID. It updates only that student's
email."

Rerun the SELECT in pgAdmin and point to `alex.new@example.com`.

## 5. Delete the student (35 seconds)

```sh
python src/students.py delete 4
```

"This calls deleteStudent. It removes the student with this ID."

Rerun the SELECT in pgAdmin. Show that only the original three students remain.

## 6. Error handling and code (40 seconds)

```sh
python src/students.py add Other Student john.doe@example.com 2023-09-04
```

"John already uses this email, so PostgreSQL does not add the new student.
The app shows an error and the table stays the same."

Show `src/students.py` and one function.

"I pass input as SQL parameters to keep it separate from the query. Changes are
saved when the query works. If it fails, the change is undone.
The README shows how to set up and run the app. Thanks for watching."

Upload the video and add its link to the README. Check that other people can
watch it. Submit the public GitHub link to the Q1 dropbox. Submit the Q2 PDF
to the Q2 dropbox.
