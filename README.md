# RIT COVID Poller

## Endpoints
- `/api/v0/latest` - retrieve the current state of the dashboard in JSON format
- `/api/v0/history` - retrieve all the prior states of the dashboard

## Setup
Locally running this application should be pretty simple.

1. (optional) Use a virtualenv
   * Why use a venv? It isolates your dependencies and helps prevent version conflicts with other projects or system dependencies.
   1. `python3 -m venv venv` will create a venv in a directory named venv
   2. `source ./venv/bin/activate` will activate the venv
2. Install dependencies
  * `pip install -r requirements.txt`
3. Run the app
  * `gunicorn poller:APP --bind=localhost:5000`
4. Scream because the database won't work because that's hard and I wrote this really poorly (rewrite soon(tm))
5. Visit localhost:5000 in your web browser.

## Linting
This demo uses pylint.
Travis CI will automatically run pylint on commits and PRs, but you can also run pylint manually, using `pylint poller`.
The pylint_quotes plugin is loaded by [the pylintrc](./.pylintrc) and will ensure standardised quotation mark formats.
