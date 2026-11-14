import argparse
import os
import sys
from dataclasses import dataclass
from datetime import date

import psycopg
from psycopg.rows import class_row


@dataclass
class Student:

    student_id: int
    first_name: str
    last_name: str
    email: str
    enrollment_date: date | None


DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=students")


def getAllStudents() -> list[Student]:
    with psycopg.connect(DATABASE_URL, row_factory=class_row(Student)) as connection:
        students = connection.execute(
            "SELECT student_id, first_name, last_name, email, enrollment_date "
            "FROM students ORDER BY student_id"
        ).fetchall()

    print("student_id | first_name | last_name | email | enrollment_date")
    for student in students:
        enrollment_date = (
            student.enrollment_date.isoformat()
            if student.enrollment_date is not None
            else "NULL"
        )
        print(
            f"{student.student_id} | {student.first_name} | {student.last_name} | "
            f"{student.email} | {enrollment_date}"
        )
    print(f"({len(students)} rows)")
    return students


def addStudent(
    first_name: str, last_name: str, email: str, enrollment_date: date | None
) -> int:
    with psycopg.connect(DATABASE_URL, row_factory=class_row(Student)) as connection:
        student, = connection.execute(
            "INSERT INTO students (first_name, last_name, email, enrollment_date) "
            "VALUES (%s, %s, %s, %s) RETURNING *",
            (first_name, last_name, email, enrollment_date),
        ).fetchall()

    print(f"Added student {student.student_id}.")
    return student.student_id


def updateStudentEmail(student_id: int, new_email: str) -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        cursor = connection.execute(
            "UPDATE students SET email = %s WHERE student_id = %s",
            (new_email, student_id),
        )
        if cursor.rowcount == 0:
            raise LookupError(f"Student {student_id} was not found.")

    print(f"Updated student {student_id}.")


def deleteStudent(student_id: int) -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE student_id = %s", (student_id,)
        )
        if cursor.rowcount == 0:
            raise LookupError(f"Student {student_id} was not found.")

    print(f"Deleted student {student_id}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="COMP 3005 student database")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Run getAllStudents()")

    add = commands.add_parser("add", help="Run addStudent()")
    add.add_argument("first_name")
    add.add_argument("last_name")
    add.add_argument("email")
    add.add_argument("enrollment_date", type=date.fromisoformat, nargs="?")

    update = commands.add_parser("update", help="Run updateStudentEmail()")
    update.add_argument("student_id", type=int)
    update.add_argument("new_email")

    delete = commands.add_parser("delete", help="Run deleteStudent()")
    delete.add_argument("student_id", type=int)
    arguments = parser.parse_args()

    try:
        if arguments.command == "list":
            getAllStudents()
        elif arguments.command == "add":
            addStudent(
                arguments.first_name,
                arguments.last_name,
                arguments.email,
                arguments.enrollment_date,
            )
        elif arguments.command == "update":
            updateStudentEmail(arguments.student_id, arguments.new_email)
        elif arguments.command == "delete":
            deleteStudent(arguments.student_id)
    except psycopg.errors.UniqueViolation:
        print("Error: that email is already assigned to a student.", file=sys.stderr)
        return 1
    except psycopg.Error as error:
        print(f"Database error: {error.diag.message_primary or str(error)}", file=sys.stderr)
        return 1
    except LookupError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
