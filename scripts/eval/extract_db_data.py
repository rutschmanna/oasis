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
    while (table_selection != "exit"):
        query = "SELECT * FROM {}".format(table_selection)
        cursor.execute(query)
        rows = cursor.fetchall()
        json_content = []

        for row in rows:
            print(" ", row)
            json_content.append(row)

        with open(f"data/db_json/{db_file[9:-3]}_{table_selection}.json", "w") as f:
            json.dump(json_content, f, indent=4)
    
        print("Tables: ", [table[0] for table in tables])
        table_selection = input("Input table to print or 'exit': ")


    conn.close()

print_db_contents(f"data/dbs/{args.db_file}")
       
