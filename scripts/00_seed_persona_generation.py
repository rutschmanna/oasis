import pandas as pd
import json

import utils.simulation_utils as su

# Load final Oswald data
sample_data = pd.read_csv(
    "../../oswald-et-al_2025/sample_anon.csv"
)
print(len(sample_data))
print(sample_data["subreddit"].unique())

# Use seed data to generate seed personas for llm agents
subreddit_personas = {}

for i in range(1, len(sample_data["subreddit"].unique()) + 1):
    subreddit_data = sample_data[sample_data["subreddit"] == f"DiscussPolitics{i}"]
    subreddit_personas[f"pf{i}"] = su.generate_personas(subreddit_data)

    with open(f"../data/reddit/pf{i}_personas.json", "w") as f:
        json.dump(subreddit_personas[f"pf{i}"], f, indent=4)

# Print number of agents per subreddit
for i in range(1, len(sample_data["subreddit"].unique()) + 1):
    print(f"pf{i}:", len(subreddit_personas[f"pf{i}"]))