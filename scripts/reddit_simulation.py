# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
import asyncio
import os
import argparse
import time
import random

from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

import oasis
from oasis import ActionType, EnvAction, SingleAction, Platform
from oasis.social_platform.channel import Channel
from oasis.social_platform.typing import RecsysType
from oasis.clock.clock import Clock

async def main():
    # Parse command line passed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", help="str model name")
    parser.add_argument("--ip", help="ip of vllm server", default="127.0.0.1")
    parser.add_argument("--port", help="port of vllm entry", default="8002")
    parser.add_argument("--time-steps", help="# of simulation steps",  type=int,  default="1")
    parser.add_argument("--print-db", help="boolean to print db", type=bool, default=False)
    args = parser.parse_args()

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
        ActionType.CREATE_POST,
        ActionType.CREATE_COMMENT,
        ActionType.LIKE_COMMENT,
        ActionType.DISLIKE_COMMENT,
        ActionType.SEARCH_POSTS,
        ActionType.SEARCH_USER,
        ActionType.TREND,
        ActionType.REFRESH,
        ActionType.DO_NOTHING,
        ActionType.FOLLOW,
        ActionType.MUTE,
    ]

    # Define the path to the database
    db_path = f"./data/dbs/reddit_sim-{args.model_name}-{time.strftime('%H-%M', time.localtime())}.db"

    env = oasis.make(
        platform=oasis.DefaultPlatformType.REDDIT,
        database_path=db_path,
        agent_profile_path="./data/reddit/test_personas.json",
        agent_models=llm_model,
        available_actions=available_actions,
    )

    # Run the environment
    await env.reset()

    action_1 = SingleAction(
            agent_id=0,
            action=ActionType.CREATE_POST,
            args={
                "content": (
                    "**Fur clothing should be banned.**\n"
                    "Please discuss! This statement serves as starting point for today’s discussion. "
                    # "It neither reflects the opinion of the researchers nor a political "
                    # "position of the research institution."
                    )
                }
            )
    
    env_action_1 = EnvAction(activate_agents=list(range(2)),
            intervention=[action_1])

    # Perform the actions
    await env.step(env_action_1)
    
    for _ in range(args.time_steps):
        env_action_empty = EnvAction(activate_agents=list(random.sample(range(110), 10)))
        await env.step(env_action_empty)

    # Close the environment
    await env.close()

    if args.print_db:
        from oasis.testing.show_db import print_db_contents
        print_db_contents(db_path)

if __name__ == "__main__":
    asyncio.run(main())
