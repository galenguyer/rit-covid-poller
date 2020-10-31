# Flask wsgi bootstrap/demo

This demo shows the use of gunicorn with flask. Original credit goes to [Max Meinhold](https://github.com/mxmeinhold/flask-gunicorn-demo).
It includes a basic Dockerfile, a linting demonstration using Pylint, and a Travis CI configuration for running linting.

This is not an in depth guide in how these tools work, but a basic starting point and reference.

Make sure to change my name and email if you use this template, especially in the license.


## Setup
Locally running this application should be pretty simple.

1. (optional) Use a virtualenv
   * Why use a venv? It isolates your dependencies and helps prevent version conflicts with other projects or system dependencies.
   1. `python3 -m venv venv` will create a venv in a directory named venv
   2. `source ./venv/bin/activate` will activate the venv
2. Install dependencies
  * `pip install -r requirements.txt`
3. Run the app
  * `gunicorn demo:APP --bind=localhost:5000`
4. Visit localhost:5000 in your web browser.

## Linting
This demo uses pylint.
Travis CI will automatically run pylint on commits and PRs, but you can also run pylint manually, using `pylint demo`.
The pylint_quotes plugin is loaded by [the pylintrc](./.pylintrc) and will ensure standardised quotation mark formats.
