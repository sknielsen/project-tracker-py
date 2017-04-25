"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
            INSERT INTO students
                VALUES (:first_name, :last_name, :github)
            """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})

    db.session.commit()
    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
        SELECT *
        FROM projects
        WHERE title = :title
        """
    db_cursor = db.session.execute(QUERY, {'title': title})
    row = db_cursor.fetchone()

    print "Project description: %s \nTotal grade: %s" % (row[2], row[3])


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """
            SELECT grade
            FROM grades
            JOIN projects
                ON grades.project_title = projects.title
            WHERE title = :title
            AND student_github = :github
            """
    db_cursor = db.session.execute(QUERY, {'title': title,
                                           'github': github})

    row = db_cursor.fetchone()
    print "Grade received: %s" % (row[0])


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""

    QUERY = """
            INSERT INTO grades (student_github, project_title, grade)
                VALUES (:student_github, :project_title, :grade)
            """
    db.session.execute(QUERY, {'student_github': github,
                               'project_title': title,
                               'grade': grade})
    db.session.commit()
    print "Successfully added grade: %s" % (grade)


def add_new_project(title, description, grade):
    """Add new project with title description and maximum grade"""

    QUERY = """
            INSERT INTO projects (title, description, max_grade)
                VALUES (:title, :description, :max_grade)
            """

    db.session.execute(QUERY, {'title': title,
                               'description': description,
                               'max_grade': grade})
    db.session.commit()
    print "Successfully added project: %s" % (title)


def get_grades_for_student(github):
    """ Show all grades for student with github given"""

    QUERY = """
            SELECT project_title, grade
            FROM grades
            WHERE student_github = :github
            """
    db_cursor = db.session.execute(QUERY, {'github': github})
    for item in db_cursor:
        print 'Title: %s, Grade: %s' % (item[0], item[1])


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade":
            github, title = args
            get_grade_by_github_title(github, title)

        elif command == "new_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        elif command == "new_project":
            title, description, grade = args
            add_new_project(title, description, grade)

        elif command == "all_grades":
            github = args[0]
            get_grades_for_student(github)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."

if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
