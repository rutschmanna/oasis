import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--db-file", help="Source Database", type=str)
args = parser.parse_args()

def print_db_contents(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables: ", [table[0] for table in tables])

    table_selection = [input("Select tables to print: ")]

    for table_name in table_selection:
        print(f"\nTable: {table_name[0]}")
        cursor.execute(f"PRAGMA table_info({table_name[0]})")
        columns = cursor.fetchall()

        for col in columns:
            print("")

print_db_contents(args.db_file)
