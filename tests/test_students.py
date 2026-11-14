import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from datetime import date
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
import students


class StudentTests(unittest.TestCase):

    def setUp(self):
        self.database_url = os.environ["TEST_DATABASE_URL"]
        self.schema = "test_students_" + uuid4().hex
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.addCleanup(self.drop_schema)
        students.DATABASE_URL = make_conninfo(
            self.database_url, options=f"-c search_path={self.schema}"
        )
        with psycopg.connect(students.DATABASE_URL, autocommit=True) as connection:
            connection.execute((PROJECT / "sql/setup.sql").read_text())

    def drop_schema(self):
        with psycopg.connect(self.database_url, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

    def test_initial_records_and_display(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            records = students.getAllStudents()
        self.assertEqual([record.student_id for record in records], [1, 2, 3])
        self.assertEqual(
            records,
            [
                students.Student(1, "John", "Doe", "john.doe@example.com", date(2023, 9, 1)),
                students.Student(2, "Jane", "Smith", "jane.smith@example.com", date(2023, 9, 1)),
                students.Student(3, "Jim", "Beam", "jim.beam@example.com", date(2023, 9, 2)),
            ],
        )
        self.assertIn("3 | Jim | Beam | jim.beam@example.com | 2023-09-02", output.getvalue())

    def test_crud_commits_between_connections(self):
        student_id = students.addStudent("Alex", "Lee", "alex@example.com", date(2023, 9, 3))
        self.assertEqual(student_id, 4)
        students.updateStudentEmail(student_id, "alex.lee@example.com")
        self.assertEqual(students.getAllStudents()[-1].email, "alex.lee@example.com")
        students.deleteStudent(student_id)
        self.assertEqual(len(students.getAllStudents()), 3)

    def test_duplicate_email_rolls_back(self):
        with self.assertRaises(psycopg.errors.UniqueViolation):
            students.addStudent("Other", "Student", "john.doe@example.com", None)
        with self.assertRaises(psycopg.errors.UniqueViolation):
            students.updateStudentEmail(2, "john.doe@example.com")
        records = students.getAllStudents()
        self.assertEqual(len(records), 3)
        self.assertEqual(records[1].email, "jane.smith@example.com")

    def test_missing_student_is_reported(self):
        with self.assertRaisesRegex(LookupError, "Student 999 was not found"):
            students.updateStudentEmail(999, "missing@example.com")
        with self.assertRaisesRegex(LookupError, "Student 999 was not found"):
            students.deleteStudent(999)

    def test_parameter_binding_and_nullable_date(self):
        name = "Robert'); DROP TABLE students; --"
        student_id = students.addStudent(name, "O'Neil", "robert@example.com", None)
        student = students.getAllStudents()[-1]
        self.assertEqual(student.first_name, name)
        self.assertIsNone(student.enrollment_date)
        students.deleteStudent(student_id)
        for original in students.getAllStudents():
            students.deleteStudent(original.student_id)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(students.getAllStudents(), [])
        self.assertIn("(0 rows)", output.getvalue())

    def test_schema_constraints(self):
        with psycopg.connect(students.DATABASE_URL, autocommit=True) as connection:
            for column in ("first_name", "last_name", "email"):
                with self.assertRaises(psycopg.errors.NotNullViolation):
                    connection.execute(
                        sql.SQL("UPDATE students SET {} = NULL WHERE student_id = 1").format(
                            sql.Identifier(column)
                        )
                    )
            with self.assertRaises(psycopg.errors.UniqueViolation):
                connection.execute("UPDATE students SET student_id = 1 WHERE student_id = 2")

    def test_cli_success_and_errors(self):
        environment = {**os.environ, "DATABASE_URL": students.DATABASE_URL}
        cases = [
            (["list"], 0, "(3 rows)"),
            (["add", "Alex", "Lee", "alex@example.com", "2023-09-03"], 0, "Added student 4"),
            (["update", "4", "alex.new@example.com"], 0, "Updated student 4"),
            (["delete", "4"], 0, "Deleted student 4"),
            (["delete", "4"], 1, "was not found"),
            (["add", "John", "Doe", "john.doe@example.com"], 1, "email is already assigned"),
            (["add", "Alex", "Lee", "alex@example.com", "2023-02-30"], 2, "invalid"),
            (["update", "wrong", "alex@example.com"], 2, "invalid int"),
        ]
        for arguments, status, message in cases:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, str(PROJECT / "src/students.py"), *arguments],
                    env=environment, text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn(message, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
