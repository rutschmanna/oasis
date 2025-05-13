import sqlite3
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--db-file", help="Source Database", type=str)
args = parser.parse_args()

def print_db_contents(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables: ", [table[0] for table in tables])

    table_selection = input("Input table to print or 'exit': ")

    query = "SELECT * FROM {}".format(table_selection)
    cursor.execute(query)
    rows = cursor.fetchall()
    json_content = []
    for row in rows:
        print(" ", row)
        json_content.append(row)

    conn.close()

    with open("data/db_json.json", "w") as f:
        json.dump(json_content, f, indent=4

                  with open("data/db_json.json", "w") as f:
                  json.dump(json_content, f, indent=4))

while True:
    try:
        print_db_contents(f"data/dbs/{args.db_file}")
    except:
        break
