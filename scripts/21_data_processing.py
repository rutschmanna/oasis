import json
import os
import pandas as pd
import numpy as np
import argparse
import pathlib

from utils.processing_utils import batch_convert_db_contents, load_db_json_data

# parse terminal arguments
parser = argparse.ArgumentParser()
parser.add_argument("--start-str", help="str of target sim directory", type=str)
parser.add_argument("--subdir", help="str of optional sub-directory", type=str, default=".")
args = parser.parse_args()

np.set_printoptions(legacy='1.25')
start_str = args.start_str

# convert .db file content to .json
batch_convert_db_contents(start_str=start_str, subdir=args.subdir)

# load df and json format of sim data
sim_discussions, sim_user, sim_trace = load_db_json_data(
    f"/../abyss/home/oasis/oasis-rutschmanna/data/db_json/{args.subdir}/",
    start_str,
    to_df=True
)

sim_discussions_json, sim_user_json, sim_trace_json = load_db_json_data(
    f"/../abyss/home/oasis/oasis-rutschmanna/data/db_json/{args.subdir}/",
    start_str
)

# mapping for the nubmer of users per sub
subreddit_mapping = {
    1: 80,
    2: 85,
    3: 85,
    4: 82,
    5: 85,
    6: 100
}

# mapping for each sub's conditon
sim_condition_mapping = {
    1: "control",
    2: "moderation",
    3: "incentives",
    4: "incentives",
    5: "moderation",
    6: "control",
}

# concatenate data into dfs
sim_discussions_data = pd.DataFrame()
sim_user_data = pd.DataFrame()
sim_trace_data = pd.DataFrame()

for i in sim_discussions.values():
    sim_discussions_data = pd.concat([sim_discussions_data, i]).reset_index(drop=True)

for i in sim_user.values():
    sim_user_data = pd.concat([sim_user_data, i]).reset_index(drop=True)

for i in sim_trace.values():
    sim_trace_data = pd.concat([sim_trace_data, i]).reset_index(drop=True)

# create additional variables
sim_discussions_data["condition"] = sim_discussions_data["subreddit"].map(sim_condition_mapping)
sim_discussions_data["sim_score_comment"] = sim_discussions_data["num_likes"] - sim_discussions_data["num_dislikes"]
sim_discussions_data["sim_comment_length"] = sim_discussions_data["content"].apply(len)

sim_discussions_data["sim_comment_count"] = sim_discussions_data.groupby("seed_user_id")["seed_user_id"].transform("size")
sim_discussions_data["sim_comment_mean_length"] = sim_discussions_data.groupby("seed_user_id")["sim_comment_length"].transform("mean").apply(int)
sim_discussions_data["sim_comment_mean_score"] = sim_discussions_data.groupby("seed_user_id")["sim_score_comment"].transform("mean").apply(lambda x: round(x, 3))

# mapping of seed subs to condition
condition_mapping = {
    "DiscussPolitics1": "control",
    "DiscussPolitics2": "moderation",
    "DiscussPolitics3": "incentives",
    "DiscussPolitics4": "incentives",
    "DiscussPolitics5": "moderation",
    "DiscussPolitics6": "control",
}

# Load seed user data and discussions data
user_data = pd.read_csv(
    "/../abyss/home/oasis/oswald-et-al_2025/sample_anon.csv",
    index_col=0
)

discussions_data = pd.read_csv(
    "/../abyss/home/oasis/oswald-et-al_2025/discussions_anon.csv",
    index_col=0
)
discussions_data["condition"] = discussions_data["subreddit"].map(condition_mapping)

discussions_data.dropna(subset="ParticipantID", inplace=True)
print("Oswald: N posts:", len(discussions_data))

# Replace NAs with 0 for further analysis (0 comments, 0 likes, etc.)
user_data = user_data[[
    "ParticipantID",
    "subreddit",
    "condition",
    "polinterest",
    "time_online",
    "social_media",
    "comments_online",
    "comment_count",
    "comment_mean_lenght",
    "comment_mean_score",
    "comment_mean_tox"
]]

user_data.rename(columns={"comment_mean_lenght":"comment_mean_length"},
                 inplace=True)

user_data.fillna(0, inplace=True)
user_data.reset_index(drop=True, inplace=True)
print(len(user_data))

# merge sim and seed user data
sim_user_data = sim_user_data.merge(user_data[[
    "ParticipantID",
    "subreddit",
    "polinterest",
    "time_online",
    "social_media",
    "comments_online"
]], how="left", left_on="user_name", right_on="ParticipantID")

sim_user_data.rename(columns={"user_name":"seed_user_id"},
                     inplace=True)

# create additional variables
sim_user_data.drop(columns="ParticipantID", inplace=True)
sim_user_data["subreddit"] = sim_user_data["subreddit"].apply(lambda x: int(x[-1]))
sim_user_data["condition"] = sim_user_data["subreddit"].map(sim_condition_mapping)
sim_user_data["n_agents"] = sim_user_data["subreddit"].map(subreddit_mapping)

# merge sim user and discussion data
sim_user_data = sim_user_data.merge(sim_discussions_data[[
    "seed_user_id",
    "sim_comment_count",
    "sim_comment_mean_length",
    "sim_comment_mean_score",
]], how="left").drop_duplicates("seed_user_id").reset_index(drop=True)

sim_user_data.fillna(0, inplace=True)

# seelct only relevant columns
sim_user_data = sim_user_data[[
    "seed_user_id",
    "user_id",
    "subreddit",
    "condition",
    "n_agents",
    "created_at",
    "polinterest",
    "time_online",
    "social_media",
    "comments_online",
    "sim_comment_count",
    "sim_comment_mean_length",
    "sim_comment_mean_score",
]]

sim_discussions_data = sim_discussions_data[[
    "seed_user_id",
    "user_id",
    "subreddit",
    "condition",
    "topic",
    "topic_content",
    "post_id",
    "comment_id",
    "parent_comment_id",
    "created_at",
    "content",
    "num_likes",
    "num_dislikes",
    "sim_score_comment",
    "sim_comment_length"
]]

sim_trace_data = sim_trace_data[[
    "seed_user_id",
    "user_id",
    "subreddit",
    "topic",
    # "topic_content",
    "action",
    "created_at",
    "info",
]]

# write data into .csv files
discussions_data = discussions_data[discussions_data["ParticipantID"].isin(sim_user_data["seed_user_id"])]
user_data = user_data[user_data["ParticipantID"].isin(sim_user_data["seed_user_id"])]

pathlib.Path(f"/../abyss/home/oasis/data/{args.subdir}").mkdir(exist_ok=True)
sim_discussions_data.to_csv(f"/../abyss/home/oasis/data/{args.subdir}/sim_discussions_data.csv",
                           index=False)
sim_user_data.to_csv(f"/../abyss/home/oasis/data/{args.subdir}/sim_user_data.csv",
                           index=False)
sim_trace_data.to_csv(f"/../abyss/home/oasis/data/{args.subdir}/sim_trace_data.csv",
                           index=False)

discussions_data["subreddit"] = discussions_data["subreddit"].apply(lambda x: int(x[-1]))
user_data["subreddit"] = user_data["subreddit"].apply(lambda x: int(x[-1]))

discussions_data.to_csv("/../abyss/home/oasis/data/seed_discussions_data.csv",
                           index=False)
user_data.to_csv("/../abyss/home/oasis/data/seed_user_data.csv",
                           index=False)
