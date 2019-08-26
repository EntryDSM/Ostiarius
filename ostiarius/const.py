from os import environ

ROOT_ADMIN = "RootAdmin"
ADMIN = "Admin"
INTERVIEWER = "Interviewer"
APPLICANT = "Applicant"

HERMES = "http://hermes"

RUN_ENV = environ.get("RUN_ENV")
GITHUB_TOKEN = environ.get("GITHUB_TOKEN")

UPLOAD_DIR = './pics'
