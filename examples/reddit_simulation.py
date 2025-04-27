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

from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

import oasis
from oasis import ActionType, EnvAction, SingleAction


async def main():
    # Parse command line passed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", help="str model type")
    parser.add_argument("--ip", help="ip of vllm server", default="127.0.0.1")
    parser.add_argument("--port", help="port of vllm entry", default="8002")
    args = parser.parse_args()

    # Define the model for the agents
    llm_model = ModelFactory.create(
        model_platform=ModelPlatformType.VLLM,
        model_type=args.model_type,
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
    db_path = "./data/reddit_simulation.db"

    # Delete the old database
    if os.path.exists(db_path):
        os.remove(db_path)

    # Make the environment
    env = oasis.make(
        platform=oasis.DefaultPlatformType.REDDIT,
        database_path=db_path,
        agent_profile_path="./data/reddit/user_data_36.json",
        agent_models=llm_model,
        available_actions=available_actions,
    )

    # Run the environment
    await env.reset()

    action_1 = SingleAction(agent_id=0,
                            action=ActionType.CREATE_POST,
                            args={"content": "Hello, world!"})
    action_2 = SingleAction(agent_id=0,
                            action=ActionType.CREATE_COMMENT,
                            args={
                                "post_id": "1",
                                "content": "Welcome to the OASIS World!"
                            })

    env_actions = EnvAction(activate_agents=list(range(20)),
                            intervention=[action_1, action_2])

    # Perform the actions
    await env.step(env_actions)

    # Close the environment
    await env.close()


if __name__ == "__main__":
    asyncio.run(main())
