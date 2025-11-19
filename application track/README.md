
# Job Application Tracker (Python CLI)

Simple, lightweight job-application tracker CLI using SQLite.

## Features
- Add, list, update, delete applications
- Export / import CSV
- Basic stats by status
- Small single-file CLI (`tracker.py`)

## Quickstart
```bash
# create a working folder and install dependencies
pip install -r requirements.txt

# initialize database
python tracker.py init

# add an application
python tracker.py add --company "ACME" --role "Software Engineer" --date "2025-11-19" --status applied --source linkedin --notes "Applied via referral"

# list
python tracker.py list

# update
python tracker.py update 1 --status interview_scheduled --notes "Phone screen on Nov 25"

# stats
python tracker.py stats

# export CSV
python tracker.py export --file myapps.csv
```

## Files
- `tracker.py` — main CLI (uses `applications.db` SQLite file)
- `README.md` — this file

## License
MIT
