import pandas as pd
import json

import utils.simulation_utils as su

# Load final Oswald data
user_data = pd.read_csv(
    "/../abyss/home/oasis/oswald-et-al_2025/sample_anon.csv"
)
print(len(user_data))
print(user_data["subreddit"].unique())

# Use seed data to generate seed personas for llm agents
subreddit_personas = {}

for i in range(1, len(user_data["subreddit"].unique()) + 1):
    subreddit_data = user_data[user_data["subreddit"] == f"DiscussPolitics{i}"]
    subreddit_personas[f"seed_personas_subreddit_{i}"] = su.generate_personas(subreddit_data, subreddit=i)

    with open(f"/../abyss/home/oasis/oasis-rutschmanna/data/reddit/seed_personas_subreddit_{i}.json", "w") as f:
        json.dump(subreddit_personas[f"seed_personas_subreddit_{i}"], f, indent=4)

# Print number of agents per subreddit
for i in range(1, len(user_data["subreddit"].unique()) + 1):
    print(f"seed_personas_subreddit_{i}:", len(subreddit_personas[f"seed_personas_subreddit_{i}"]))