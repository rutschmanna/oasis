import os
import sqlite3
import json
import re
import pathlib
import pandas as pd
import numpy as np
from scipy.stats import norm, chi2
from googleapiclient import discovery
import time
from tqdm import tqdm
import utils.simulation_utils as su

seed_posts = {
        1: "The US should condemn Israel’s military actions in Gaza as acts of genocide and impose full sanctions.",
        2: "Prostitution should be illegal.",
        3: "Things like gender-neutral language and stating pronouns are silly issues.",
        4: "The death penalty should be reestablished US-wide.",
        5: "The US should provide financial and military aid to Ukraine.",
        6: "We need stricter gun control laws.",
        7: "Social media is a threat to democracy.",
        8: "Immigration should be regulated more strictly.",
        9: "Fur clothing should be banned.",
        10: "Police officers should wear body cameras.",
        11: "Climate change is one of the greatest threats to humanity.",
        12: "Employers should mandate vaccination.",
        13: "The government should not be responsible for providing universal health care.",
        14: "The government should not forgive student loan debt.",
        15: "Artificial intelligence should replace humans where possible.",
        16: "There should only be vegetarian food in cantines.",
        17: "A universal basic income would kill the economy.",
        18: "The federal minimum wage should be increased.",
        19: "The government should not invest in renewable energy.",
        20: "Airbnb should be banned in cities."
    }

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

def batch_convert_db_contents(
    start_str,
    base_path="/../abyss/home/oasis/oasis-rutschmanna/data",
):
    
    db_path = f"{base_path}/dbs/"
    
    db_directory = os.fsencode(db_path)    
    for simulation_dir in os.listdir(db_directory):
        simulation_name = os.fsdecode(simulation_dir)
    
        if simulation_name.startswith(start_str):
            print("Connecting to", simulation_name)
            db_directory_path = f"{db_path}{simulation_name}/"

            for seed_post_db in os.listdir(db_directory_path):
                db_file_name = os.fsdecode(seed_post_db)
                db_file_path = f"{db_directory_path}{db_file_name}"
                
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
            
                    pathlib.Path(f"{base_path}/db_json/{simulation_name}").mkdir(exist_ok=True)
                    pathlib.Path(f"{base_path}/db_json/{simulation_name}/{db_file_name[:-3]}").mkdir(exist_ok=True)
                    
                    with open(
                        f"{base_path}/db_json/{simulation_name}/{db_file_name[:-3]}/{table_name}.json", "w"
                    ) as f:
                        json.dump(db_content, f, indent=4)
                
                print(f"Tables saved at {base_path}/db_json/{simulation_name}/{db_file_name[:-3]}/")
            
            
                conn.close()

def load_db_json_data(db_json_path, start_str="reddit-sim_",
                      to_df=False):
    data = {}
    trace_data = {}
    
    directory = os.fsencode(db_json_path)   
    for subdir in os.listdir(directory):
        simulation_name = os.fsdecode(subdir)
    
        if simulation_name.startswith(start_str):
            print("Reading: ", simulation_name)

            df_content = pd.DataFrame()
            json_content = []
            trace_df = pd.DataFrame()
            trace_json = []
            
            seed_post_directory = f"{db_json_path}{simulation_name}/"
            for seed_post_dir in os.listdir(seed_post_directory):
                seed_post_name = os.fsdecode(seed_post_dir)
            
                with open(f"{db_json_path}{simulation_name}/{seed_post_name}/comment.json") as f:
                    content = json.load(f)
            
                with open(f"{db_json_path}{simulation_name}/{seed_post_name}/user.json") as f:
                    users = json.load(f)

                with open(f"{db_json_path}{simulation_name}/{seed_post_name}/trace.json") as f:
                    trace = json.load(f)
    
                for i in content:
                    for j in users:
                        if i["user_id"] == j["user_id"]:
                            i["seed_user_id"] = j["user_name"]
                    i["subreddit"] = int(re.findall(r"(?<=subreddit-)\d+", simulation_name)[0])
                    seed_post_n = int(re.findall(r"\d+", seed_post_name)[0])
                    i["seed_post"] = seed_post_n
                    i["seed_post_content"] = seed_posts[seed_post_n]


                if to_df:
                    df_content = pd.concat([df_content, pd.DataFrame(content)])
                    trace_df = pd.concat([trace_df, pd.DataFrame(trace)])
                else:
                    # return content
                    json_content.extend(content)
                    trace_json.extend(trace)
                
            if to_df:
                data[simulation_name] = df_content.sort_values(
                    ["seed_post", "created_at"]
                ).reset_index(drop=True)
                trace_data[simulation_name] = trace_df.sort_values(
                    ["created_at"]
                ).reset_index(drop=True)
            else:
                data[simulation_name] = json_content
                trace_data[simulation_name] = trace_json

    return data, trace_data
    
# def load_db_json_data(db_json_path, start_str="reddit-sim_", 
#                       multi_sim=False,
#                       to_df=False):
#     data = {}
    
#     directory = os.fsencode(db_json_path)   
#     for subdir in os.listdir(directory):
#         name = os.fsdecode(subdir)
    
#         if name.startswith(start_str):
#             print("Reading: ", name)
#             with open(f"{db_json_path}{name}/comment.json") as f:
#                 content = json.load(f)
        
#             with open(f"{db_json_path}{name}/user.json") as f:
#                 users = json.load(f)

#             n_topics = 1
#             for i in content:
#                 n_topics = (
#                     i["post_id"] if i["post_id"] > n_topics else n_topics
#                 )
#                 for j in users:
#                     if i["user_id"] == j["user_id"]:
#                         i["seed_user_id"] = j["user_name"]
#                 # i["subreddit"] = re.findall(r"(?<=pf)\d+", name)[0]
#                 i["subreddit"] = re.findall(r"pf\d+", name)[0]

#             if n_topics > 1 and multi_sim == True:
#                 multi_sim_content = {}
#                 multi_sim_content["n_topics"] = n_topics
#                 for i in range(1, n_topics+1):
#                     single_topic_content = []
#                     for j in content:
#                         if i == j["post_id"]:
#                             single_topic_content.append(j)
#                     multi_sim_content[f"topic_{i}"] = single_topic_content
#                 if to_df:
#                     data[name] = pd.DataFrame(multi_sim_content)
#                 else:
#                     data[name] = multi_sim_content
                
#             else:
#                 if to_df:
#                     data[name] = pd.DataFrame(content)
#                 else:
#                     data[name] = content

#     return data

def structure_analysis(data, n=-1, root_id="parent_comment_id"):
    if isinstance(data, pd.DataFrame):
        return structure_analysis_df(data, root_id)
    else:
        if n == -1:
            print("Please pass valid n argument!")
        else:
            return structure_analysis_json(data, n, root_id)

def structure_analysis_json(data, n, root_id="parent_comment_id"):

    # Interaction Volume
    volume = len(data)
    
    # Structural width analysis
    width = 0
    for i in data:
        if i[root_id] == -1:
            width += 1
            
    # Structural depth analysis
    depth = recursive_depth_json(data)

    # Scale
    temp = []
    for i in data:
        if i["user_id"] not in temp:
            temp.append(i["user_id"]) 
    scale = len(temp)

    # Active share
    active = round(len(temp) / n, 3)

    # Comment Lengths
    comment_lengths = []
    for i in data:
        comment_lengths.append(len(i["content"]))
                

    return volume, width, depth, scale, active, comment_lengths

def structure_analysis_df(data, root_id="parent_comment_id"):
    
    # Interaction Volume
    volume = data.groupby(
        ["subreddit", "seed_post"]
    ).count().iloc[:,0].tolist()
    
    # Structural width analysis
    temp = data[data["parent_comment_id"] == -1]
    width = temp.groupby(["subreddit", "seed_post"]).count().iloc[:,0].tolist()
            
    # Structural depth analysis
    depth = []
    for i, j in data.groupby(["subreddit", "seed_post"]):
        temp = recursive_depth_df(j)
        depth.append(temp)

    # Scale
    scale = data.groupby(
        ["subreddit", "seed_post"]
    )["user_id"].unique().apply(len).tolist()

    # Active share
    n = [i[0].item() for i in data.groupby(
        ["subreddit", "seed_post"]
    )["n_agents"].unique()]
    active = [round(i / j, 3) for i,j in zip(scale, n)]

    # Comment Lengths
    comment_lengths = data.groupby(
        ["subreddit", "seed_post"]
    )["content"].apply(lambda x: [len(i) for i in x]).tolist()
                

    return volume, width, depth, scale, active, comment_lengths

def recursive_depth_json(data, parent_comment_id=-1, current_depth=0,
                   id_col="comment_id", root_col="parent_comment_id"):
    max_depth = current_depth
    for entry in data:
        entry_id = entry[id_col]
        if parent_comment_id == -1:
            depth = recursive_depth_json(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
        elif entry[root_col] == parent_comment_id:
            depth = recursive_depth_json(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
            
    return max_depth

def recursive_depth_df(data, parent_comment_id=-1, current_depth=0,
                   id_col="comment_id", root_col="parent_comment_id"):
    max_depth = current_depth
    for i, entry in data.iterrows():
        entry_id = entry[id_col]
        if parent_comment_id == -1:
            depth = recursive_depth_df(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
        elif entry[root_col] == parent_comment_id:
            depth = recursive_depth_df(data, entry_id, current_depth + 1)
            if depth > max_depth:
                max_depth = depth
            
    return max_depth

def fisher(data):
    log_p = np.sum(np.log(data["p"]))
    X2 = -2 * log_p
    p_value_fisher = 1 - chi2.cdf(X2, 2 * len(data["p"]))

    mean_stat = np.mean(data["stat"])
    
    return mean_stat, p_value_fisher

def query_perspective_json(data, api_key):
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

def query_perspective_df(data, content_col, api_key):
    data = data.copy()
    client = discovery.build(
      "commentanalyzer",
      "v1alpha1",
      developerKey=api_key,
      discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
      static_discovery=False,
    )

    perspective_results = []
    for i in tqdm(data[content_col]):
        req = {
            "comment": {"text": i},
            "requestedAttributes": {"TOXICITY": {}}
        }
        
        resp = client.comments().analyze(body=req).execute()
        perspective_results.append(resp["attributeScores"]["TOXICITY"]["summaryScore"]["value"])
        time.sleep(1) # quota limit of 60 reqs per min

    data[f"{content_col}_toxicity"] = perspective_results

    return data    