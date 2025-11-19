
#!/usr/bin/env python3
"""
Job Application Tracker - CLI
Usage:
  python tracker.py add --company "ACME" --role "SWE" --date 2025-11-01 --status applied
  python tracker.py list --status applied
  python tracker.py update 1 --status interviewed --notes "Phone screen scheduled"
  python tracker.py stats
  python tracker.py export --file applications.csv
"""
import argparse
import sqlite3
import csv
from datetime import datetime
from tabulate import tabulate

DB = "applications.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    date_applied TEXT,
    status TEXT,
    source TEXT,
    salary TEXT,
    notes TEXT,
    last_updated TEXT
);
"""

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def add_application(args):
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO applications (company, role, location, date_applied, status, source, salary, notes, last_updated) VALUES (?,?,?,?,?,?,?,?,?)",
        (args.company, args.role, args.location, args.date, args.status, args.source, args.salary, args.notes, now)
    )
    conn.commit()
    conn.close()
    print("Added application for", args.company)

def list_applications(args):
    conn = get_conn()
    q = "SELECT * FROM applications"
    filters = []
    params = []
    if args.status:
        filters.append("status = ?")
        params.append(args.status)
    if args.company:
        filters.append("company LIKE ?")
        params.append(f"%{args.company}%")
    if filters:
        q += " WHERE " + " AND ".join(filters)
    q += " ORDER BY date_applied DESC"
    cur = conn.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    if rows:
        print(tabulate([tuple(r) for r in rows], headers=rows[0].keys()))
    else:
        print("No applications found.")

def update_application(args):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM applications WHERE id = ?", (args.id,))
    row = cur.fetchone()
    if not row:
        print("No application with id", args.id)
        return
    updates = {}
    for fld in ("company","role","location","date","status","source","salary","notes"):
        val = getattr(args, fld) if hasattr(args, fld) else None
        if val:
            col = "date_applied" if fld=="date" else fld
            updates[col] = val
    if not updates:
        print("No updates provided.")
        return
    updates["last_updated"] = datetime.utcnow().isoformat()
    set_sql = ", ".join([f"{k}=?" for k in updates.keys()])
    params = list(updates.values()) + [args.id]
    conn.execute(f"UPDATE applications SET {set_sql} WHERE id = ?", params)
    conn.commit()
    conn.close()
    print("Updated application", args.id)

def stats(args):
    conn = get_conn()
    cur = conn.execute("SELECT status, COUNT(*) as cnt FROM applications GROUP BY status")
    rows = cur.fetchall()
    conn.close()
    if rows:
        print(tabulate(rows, headers=["Status","Count"]))
    else:
        print("No data to show.")

def export_csv(args):
    conn = get_conn()
    cur = conn.execute("SELECT * FROM applications ORDER BY date_applied DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No data to export.")
        return
    with open(args.file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for r in rows:
            writer.writerow(tuple(r))
    print("Exported to", args.file)

def import_csv(args):
    conn = get_conn()
    with open(args.file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                "INSERT INTO applications (company, role, location, date_applied, status, source, salary, notes, last_updated) VALUES (?,?,?,?,?,?,?,?,?)",
                (row.get("company"), row.get("role"), row.get("location"), row.get("date_applied"), row.get("status"), row.get("source"), row.get("salary"), row.get("notes"), datetime.utcnow().isoformat())
            )
    conn.commit()
    conn.close()
    print("Imported CSV:", args.file)

def delete_application(args):
    conn = get_conn()
    conn.execute("DELETE FROM applications WHERE id = ?", (args.id,))
    conn.commit()
    conn.close()
    print("Deleted application", args.id)

def main():
    parser = argparse.ArgumentParser(description="Job Application Tracker")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init")
    p_init.set_defaults(func=lambda args: init_db())

    p_add = sub.add_parser("add")
    p_add.add_argument("--company", required=True)
    p_add.add_argument("--role", required=True)
    p_add.add_argument("--location", default="")
    p_add.add_argument("--date", default="")
    p_add.add_argument("--status", default="applied")
    p_add.add_argument("--source", default="")
    p_add.add_argument("--salary", default="")
    p_add.add_argument("--notes", default="")
    p_add.set_defaults(func=add_application)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status", default=None)
    p_list.add_argument("--company", default=None)
    p_list.set_defaults(func=list_applications)

    p_update = sub.add_parser("update")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--company")
    p_update.add_argument("--role")
    p_update.add_argument("--location")
    p_update.add_argument("--date")
    p_update.add_argument("--status")
    p_update.add_argument("--source")
    p_update.add_argument("--salary")
    p_update.add_argument("--notes")
    p_update.set_defaults(func=update_application)

    p_stats = sub.add_parser("stats")
    p_stats.set_defaults(func=stats)

    p_export = sub.add_parser("export")
    p_export.add_argument("--file", default="applications.csv")
    p_export.set_defaults(func=export_csv)

    p_import = sub.add_parser("import")
    p_import.add_argument("--file", required=True)
    p_import.set_defaults(func=import_csv)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("id", type=int)
    p_delete.set_defaults(func=delete_application)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
