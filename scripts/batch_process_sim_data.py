import os
import argparse
from processing_utils import convert_db_contents

parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", help="Data Direcory Name", type=str)
args = parser.parse_args()

directory = os.fsencode(args.data_dir)

for db in os.listdir(directory):
    db_name = os.fsdecode(db)

    if db_name.endswith(".db"):
        print("Converting db: ", db_name)
        convert_db_contents(db_name)
    else:
        continue