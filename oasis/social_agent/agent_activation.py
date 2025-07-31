# custom
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
import scipy.stats
import numpy as np
import os
import logging
import sys

log_dir = "./log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if "sphinx" not in sys.modules:
    activation_log = logging.getLogger(name="agent-activation")
    activation_log.setLevel("DEBUG")
    now = datetime.now().strftime("%m-%d")
    file_handler = logging.FileHandler(f"./log/agent_activation-{now}.log")
    file_handler.setLevel("DEBUG")
    file_handler.setFormatter(
        logging.Formatter(
            "%(levelname)s - %(asctime)s - %(name)s - %(message)s"))
    activation_log.addHandler(file_handler)

def activation_function(
    data,
    db_path,
    env,
    mapping_type,
    distribution_fit,
    joined_agents,
    print_info=True,
    initiation_ie_time=90,
    inter_burst_time=90*3,
):
    """
    Determines the activation of LLM agents in the OASIS simulation.
    Each agent is assigned a probability of activation depending
    on the seed user's self reported online behavior.

    Parameters
    data: seed user data (contains self-reported online behavior)
        indexed by ParticipantID (seed_id)
    db_path: path to OASIS simulation data base
    """
    
    current_time = env.sandbox_clock.time_transfer(
                datetime.now(), env.start_time)
    
    if mapping_type == "comments":
        mapping = {
            1: 0.005,  # never
            2: 0.0075, # once per month
            3: 0.03,   # once per week
            4: 0.05,   # almost daily
            5: 0.1,    # multiple times a day
        }
        
    elif mapping_type == "rare_comments":
        mapping = {
            1: 0.0025,  # never
            2: 0.00325, # once per month
            3: 0.015,   # once per week
            4: 0.025,   # almost daily
            5: 0.05,    # multiple times a day
        }
        
    elif mapping_type == "very_rare_comments":
        mapping = {
            1: 0.0005,  # never
            2: 0.00075, # once per month
            3: 0.003,   # once per week
            4: 0.01,   # almost daily
            5: 0.025,    # multiple times a day
        }
        
    elif mapping_type == "social_media": # very high!
        mapping = {
            1: 0.01, # not at all
            2: 0.03, # a couple of times per week
            3: 0.08, # about once per day
            4: 0.12, # multiple times per day
            5: 0.15, # almost constantly
        }
    
    # Create empty list to hold IDs of activated agents
    activated_agents_step = []

    # Access content from "live" db
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    activation_log.info(f"{len(joined_agents)} Agents received from Sim-Script")
    _ = ','.join(['?'] * len(joined_agents))
    query = f"SELECT user_id, user_name FROM user WHERE user_name IN ({_})"
    # User data
    cursor.execute(query, joined_agents)

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    db_content = [dict(zip(columns, row)) for row in rows]

    # Comment data
    cursor.execute("SELECT user_id, created_at FROM comment")

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    previous_activations = [dict(zip(columns, row)) for row in rows]
    
    conn.close()

    activated_agents = {}
    disconnected_agents = []

    for i in previous_activations:
        timestamp_str = i["created_at"]
        timestamp = datetime.fromisoformat(timestamp_str)
        if i["user_id"] not in activated_agents.keys():
            activated_agents[i["user_id"]] = [timestamp]
        else:
            activated_agents[i["user_id"]].append(timestamp)
    
    # Decide agent activation
    activation_log.info(f"{len(db_content)} Agents passed to Activation")
    for i in db_content:
        i["comments_online"] = data.at[i["user_name"], "comments_online"]
        i["activation_prob"] = mapping[i["comments_online"]]
        try:
            last_initiation = activated_agents[i["user_id"]][-1]
            for j in activated_agents[i["user_id"]][::-1]:
                if last_initiation - j <= timedelta(minutes=initiation_ie_time):
                    last_initiation = j
                else:
                    break
            i["last_initiation"] = last_initiation
        except:
            i["last_initiation"] = datetime(1970, 1, 1, 0, 0, 0)

        activation_threshold = random.random()
        inter_event_difference = current_time - i["last_initiation"]
        if i["user_id"] not in activated_agents.keys() and inter_event_difference <= timedelta(minutes=inter_burst_time):
            activation_prob = i["activation_prob"] 
            i["activated"] = (
                True if activation_threshold < activation_prob else False
            )

        elif i["user_id"] in activated_agents.keys() and inter_event_difference > timedelta(hours=12):
            i["activated"] = False
            disconnected_agents.append(i["user_id"])
        
        else:
            x_prelim = (current_time - i["last_initiation"]).total_seconds() - 60*60

            if x_prelim < distribution_fit.xmin:
                x = distribution_fit.xmin
            elif distribution_fit.xmax != None:
                if x_prelim > distribution_fit.xmax:
                    x = distribution_fit.xmax
            else:
                x = x_prelim

            recurring_activation_prob = distribution_fit.ccdf(
                x
            ) #* recurring_activation_prob_modifier
            
            activation_prob = i["activation_prob"] + recurring_activation_prob
            
            i["activated"] = (
                True if activation_threshold < activation_prob else False
            )
        
        if i["activated"] == True:
            activated_agents_step.append(i["user_id"])

    activation_log.info(f"{len(activated_agents_step)} Agents activated:\n{activated_agents_step}")
    activation_log.info(f"{len(disconnected_agents)} Agents disconnected:\n{disconnected_agents}")
    if print_info:
        print("#" * 80)      
        print("Activation function activated:", len(activated_agents_step), "users.")
        print("#" * 80)
    return activated_agents_step, disconnected_agents
# custom