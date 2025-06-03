import sqlite3
import json
import pathlib
import numpy as np
from scipy.stats import norm, chi2
from googleapiclient import discovery
import time
from tqdm import tqdm
import utils.simulation_utils as su


def convert_db_contents(db_file,
                        base_path="/../abyss/home/oasis/oasis-rutschmanna/data"):
    
    db_file_path = f"{base_path}/dbs/{db_file}"
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    for table_name in table_names:
        query = "SELECT * FROM {}".format(table_name)
        cursor.execute(query)
        
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        db_content = [dict(zip(columns, row)) for row in rows]

        pathlib.Path(f"{base_path}/db_json/{db_file[:-3]}").mkdir(exist_ok=True)
        
        with open(
            f"{base_path}/db_json/{db_file[:-3]}/{table_name}.json", "w"
        ) as f:
            json.dump(db_content, f, indent=4)
    
    print(f"Tables saved at {base_path}/db_json/{db_file[:-3]}/")


    conn.close()

def structure_analysis(data, n, root_id="parent_comment_id"):

    # Interaction Volume
    volume = len(data)
    
    # Structural width analysis
    width = 0
    for i in data:
        if i[root_id] == -1:
            width += 1
            
    # Structural depth analysis
    depth = recursive_depth(data)

    # Scale
    temp = []
    for i in data:
        if i["user_id"] not in temp:
            temp.append(i["user_id"]) 
    scale = len(temp)

    # Active share
    active = len(temp) / n

    # Comment Lengths
    comment_lengths = []
    for i in data:
        comment_lengths.append(len(i["content"]))
                

    return volume, width, depth, scale, active, comment_lengths

def recursive_depth(data, parent_comment_id=-1, current_depth=0,
                   id_col="comment_id", root_col="parent_comment_id"):
    max_depth = current_depth
    for entry in data:
        entry_id = entry[id_col]
        if parent_comment_id == -1:
            depth = recursive_depth(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
        elif entry[root_col] == parent_comment_id:
            depth = recursive_depth(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
            
    return max_depth

def fisher(data):
    log_p = np.sum(np.log(data["p"]))
    X2 = -2 * log_p
    p_value_fisher = 1 - chi2.cdf(X2, 2 * len(data["p"]))

    mean_stat = np.mean(data["stat"])
    
    return mean_stat, p_value_fisher

def query_perspective(data, api_key):
    client = discovery.build(
      "commentanalyzer",
      "v1alpha1",
      developerKey=api_key,
      discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
      static_discovery=False,
    )
    
    for i in tqdm(data):
        req = {
            "comment": {"text": i["content"]},
            "requestedAttributes": {"TOXICITY": {}}
        }
        
        resp = client.comments().analyze(body=req).execute()
        i["toxicity"] = resp["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
        time.sleep(1) # quota limit of 60 reqs per min

    return data