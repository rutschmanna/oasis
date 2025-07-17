import asyncio
import os
import argparse
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
import powerlaw

from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

import oasis
from oasis import ActionType, EnvAction, SingleAction, Platform
from oasis.social_agent.agent_activation import activation_function
from oasis.social_platform.channel import Channel
from oasis.clock.clock import Clock

# Parse command line passed arguments
parser = argparse.ArgumentParser()
parser.add_argument("--model-name", help="str model name")
parser.add_argument("--ip", help="ip of vllm server", default="127.0.0.1")
parser.add_argument("--port", help="port of vllm entry", default="8002")
parser.add_argument("--time-steps", help="# of simulation steps",  type=int,  default=3)
parser.add_argument("--subreddit", help="file containing personas", type=int, default=1)
parser.add_argument("--topic", help="int key for respective seed post", type=int, default=1)
parser.add_argument("--clock-factor", help="int value for sandbox time modificator", type=int, default=60)
parser.add_argument("--base-activation-mapping", help="'comment', 'rare_comment', 'very_rare_comment'", type=str, default="comments")
args = parser.parse_args()


log_dir = "./log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if "sphinx" not in sys.modules:
    script_log = logging.getLogger(name="11_reddit_sim")
    script_log.setLevel("DEBUG")
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_handler = logging.FileHandler(f"./log/11_reddit_sim-{datetime.now().strftime('%m-%d')}.log")
    file_handler.setLevel("DEBUG")
    file_handler.setFormatter(
        logging.Formatter(
            "%(levelname)s - %(asctime)s - %(message)s"))
    script_log.addHandler(file_handler)

async def main():
    # Define the model for the agents
    llm_model = ModelFactory.create(
        model_platform=ModelPlatformType.VLLM,
        model_type=args.model_name,
	    url=f"http://{args.ip}:{args.port}/v1",
    )

    # Define the available actions for the agents
    available_actions = [
        ActionType.LIKE_POST,
        ActionType.DISLIKE_POST,
        ActionType.UNLIKE_POST,
        ActionType.UNDO_DISLIKE_POST,
        # ActionType.CREATE_POST,
        ActionType.CREATE_COMMENT,
        ActionType.LIKE_COMMENT,
        ActionType.DISLIKE_COMMENT,
        ActionType.UNLIKE_COMMENT,
        ActionType.UNDO_DISLIKE_COMMENT,
        ActionType.CREATE_COMMENT_COMMENT,
        # ActionType.SEARCH_POSTS,
        # ActionType.SEARCH_USER,
        # ActionType.TREND,
        # ActionType.REFRESH,
        ActionType.DO_NOTHING,
        # ActionType.FOLLOW,
        # ActionType.MUTE,
        # ActionType.UNMUTE,
    ]

    time_factor = 60/args.clock_factor
    time_steps = int(args.time_steps*time_factor)
    db_dir_path = f"/../abyss/home/oasis/oasis-rutschmanna/data/dbs/reddit-sim_{args.model_name}_subreddit-{args.subreddit}-{args.time_steps}h/" # _{time.strftime('%H-%M', time.localtime())}

    script_log.info(f"Time factor: {time_factor}")
    script_log.info(f"Time steps: {args.time_steps}")
    script_log.info(f"Factored Time stepes {time_steps}")
    
    if not os.path.exists(db_dir_path):
        os.makedirs(db_dir_path)
        print("Created:", db_dir_path)

    # Define the path to the database
    db_path = f"{db_dir_path}topic_{args.topic}.db"

    # Load Oswald et al. sample data and fit powerlaw
    sample_data = pd.read_csv("/../abyss/home/oasis/oswald-et-al_2025/sample_anon.csv")
    interevent_data_seed = pd.read_csv(
        "/../abyss/home/oasis/data/intraevent.csv"
    )["interevent_diff"]
    fit = powerlaw.Fit(
        xmin=interevent_data_seed.min(), 
        xmax=interevent_data_seed.max(), 
        data=interevent_data_seed
    )
    distribution_fit = fit.lognormal

    # env = oasis.make(
    #     platform=oasis.DefaultPlatformType.REDDIT
    #     database_path=db_path,
    #     agent_profile_path=f"data/reddit/dp{args.persona_file}_personas.json",
    #     agent_models=llm_model,
    #     available_actions=available_actions,
    # )

    env = oasis.make(
        platform=Platform(
            db_path=db_path,
            channel=Channel(),
            recsys_type="reddit",
            allow_self_rating=True,
            show_score=True,
            max_rec_post_len=10000,
            sandbox_clock=Clock(args.clock_factor),
            start_time=datetime(2025, 7, 1, 12, 00, 00) + timedelta(hours=24*(args.topic-1)),
        ),
        database_path=db_path,
        agent_profile_path=f"data/reddit/seed_personas_subreddit_{args.subreddit}.json",
        agent_models=llm_model,
        available_actions=available_actions,
        semaphore=16,
    )

    topics = {
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

    # Run the environment
    await env.reset()

    action_1 = SingleAction(
            agent_id=0,
            action=ActionType.CREATE_POST,
            args={
                "content": (
                    f"{topics[args.topic]}\n"
                    "Please discuss! This statement serves as starting point for today’s discussion."
                    # "It neither reflects the opinion of the researchers nor a political "
                    # "position of the research institution."
                    )
                }
            )

    activated_agents = [0]
    env_action_1 = EnvAction(
        activate_agents=activated_agents,
        intervention=[action_1]
    )

    # Perform the actions
    script_log.info(f"{len(activated_agents)} agents activated")
    script_log.info(f"Seed post - Intervention executed")
    await env.step(env_action_1)
    
    for _ in range(time_steps):
        script_log.info(f"Time step {_+1} initiated - {env.platform.sandbox_clock.time_transfer(datetime.now(), env.platform.start_time)}")
        activated_agents, disconnected_agents = activation_function(
            sample_data.set_index("ParticipantID"),
            db_path,
            env.platform,
            mapping_type=args.base_activation_mapping,
            distribution_fit=distribution_fit,
        )

        if len(activated_agents) > 0:
            env_action_empty = EnvAction(
                activate_agents=activated_agents
            )
            script_log.info(f"{len(activated_agents)} agents activated")
            script_log.info(f"{len(disconnected_agents)} agents activated: {disconnected_agents}")
            await env.step(env_action_empty)
        else:
            sleep = random.randint(
                int((time_factor*0.8)*60),
                int(time_factor*60)
            )
            script_log.info(f"No agents activated - Sleep for {sleep}s")
            time.sleep(sleep)

    # Close the environment
    await env.close()

if __name__ == "__main__":
    script_log.info("#"*80)
    script_log.info("Initialized")
    script_log.info("#"*80)
    asyncio.run(main())
    script_log.info("#"*80)
    script_log.info("Done")
    script_log.info("#"*80)