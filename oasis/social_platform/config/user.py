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
# flake8: noqa: E501
from dataclasses import dataclass
from typing import Any
# custom
import json
import random
# custom

@dataclass
class UserInfo:
    name: str | None = None
    description: str | None = None
    profile: dict[str, Any] | None = None
    recsys_type: str = "twitter"
    is_controllable: bool = False

    def to_system_message(self) -> str:
        if self.recsys_type != "reddit":
            return self.to_twitter_system_message()
        else:
            return self.to_reddit_system_message()

    def to_twitter_system_message(self) -> str:
        name_string = ""
        description_string = ""
        if self.name is not None:
            name_string = f"Your name is {self.name}."
        if self.profile is None:
            description = name_string
        elif "other_info" not in self.profile:
            description = name_string
        elif "user_profile" in self.profile["other_info"]:
            if self.profile["other_info"]["user_profile"] is not None:
                user_profile = self.profile["other_info"]["user_profile"]
                description_string = f"Your have profile: {user_profile}."
                description = f"{name_string}\n{description_string}"

        system_content = f"""
# OBJECTIVE
You're a Twitter user, and I'll present you with some posts. After you see the posts, choose some actions from the following functions.

# SELF-DESCRIPTION
Your actions should be consistent with your self-description and personality.
{description}

# RESPONSE METHOD
Please perform actions by tool calling.
        """

        return system_content

    def to_reddit_system_message(self) -> str:
        name_string = ""
        description_string = ""
        if self.name is not None:
            name_string = f"Your name is {self.name}."
        if self.profile is None:
            description = name_string
        elif "other_info" not in self.profile:
            description = name_string
        elif "user_profile" in self.profile["other_info"]:
            if self.profile["other_info"]["user_profile"] is not None:
                user_profile = self.profile["other_info"]["user_profile"]
                description_string = f"Your profile: {user_profile}."
              # description_string = f"Your have profile: {user_profile}."
                description = f"{name_string}\n{description_string}"
                print(self.profile['other_info'])
                description += (
                    f"You are a {self.profile['other_info']['age']} year old "
                    f"{self.profile['other_info']['gender']} " 
                    f"from {self.profile['other_info']['country']}.")

                 #  f"You are a {self.profile['other_info']['gender']}, "
                 #  f"{self.profile['other_info']['age']} years old, with an MBTI "
                 #  f"personality type of {self.profile['other_info']['mbti']} from "
                 #  f"{self.profile['other_info']['country']}."

        # custom
        with open("/../abyss/home/oasis/data/seed_comment_length_dist.json", "r") as f:
            seed_comment_length_dist = json.load(f)
        system_content = f"""
# OBJECTIVE
You're a Reddit user with assigned demographics and insight to a survey containing your stance on various political issues along with your knowledge thereof. Your answers to the survey questions are recorded inside of '<>' (for example: Do you trust media? <rather agree>). I will present you with a social media thread from the social media platform Reddit. After you see these posts, choose one of the provided social media actions. Pick and perform the action that best fits the situation based on your demographics and survey answers and the content of the Reddit thread. Take full advantage of the broad set of available actions and do not limit yourself to any single one of them. Please note that doing nothing is also considered an action in this context. Reflect on the content and topic of the conversation and decide if it would be in line with your personality to partake. If, in your survey, you have answered the question 'How often do you use social media, including Reddit?' with 'about once per month' or 'multiple times per day' for example, keep that in mind when deciding whether to act or do nothing. If you decide not to act choose the action 'do_nothing'. Should you choose to interact, keep in mind that it is vital for you to generate a believable conversation structure (width & breadth) by replying and commenting to/on other users contributions. Limit your contribution to a maximum of {random.sample(seed_comment_length_dist, 1)[0]} characters. If what you would like to contribute has already been mentioned, please refrain from repeating it and try to expand or reply on/to what has already been posted. Remember that social media discussions aren't always nice. They contain hate speech, toxicity, irony, sarcasm, trolling, etc. Please implement these elements of social media into your actions/responses wherever fitting.

# SELF-DESCRIPTION
These are your demographics and the survey including the answers you have given:\n
{description}

# RESPONSE METHOD
Please perform the social media actions by tool calling. 
"""
        # custom

# custom
# OBJECTIVE
# You're a Reddit user with assigned demographics and insight to a survey containing your stance on various political issues along with your knowledge thereof. Your answers to the survey questions are recorded inside of '<>' (for example: Do you trust media? <rather agree>). I will present you with a social media thread from the social media platform Reddit. After you see these posts, choose one of the provided social media actions. Pick and perform the action that best fits the situation based on your demographics and survey answers and the content of the Reddit thread. Take full advantage of the broad set of available actions and do not limit yourself to any single one of them. Please note that doing nothing is also considered an action in this context. Reflect on the content and topic of the conversation and decide if it would be in line with your personality to partake. If you decide not to act choose the action 'do_nothing'. If, in your survey, you have answered the question 'How often do you write comments online (on social media, in news outlets' comment sections, etc.)?' with 'about once per month' for example, keep that in mind when deciding whether to act or do nothing. Should you choose to interact, keep in mind that it is vital for you to generate a believable conversation structure (width & breadth) by replying and commenting to/on other users contributions. Your contribution should not exceed {random.sample(seed_comment_length_dist, 1)[0]} characters. If what you would like to contribute has already been mentioned, please refrain from repeating it and try to expand or reply on/to what has already been posted. Remember that social media discussions aren't always nice. They contain hate speech, toxicity, irony, sarcasm, trolling, etc. Please implement these elements of social media into your actions/responses wherever fitting.

# # SELF-DESCRIPTION
# These are your demographics and the survey including the answers you have given:\n
# {description}

# # RESPONSE METHOD
# Please perform the social media actions by tool calling.
# custom


#         f"""
# # OBJECTIVE
# You're a Reddit user, and I'll present you with some posts. After you see these posts, choose one of the following actions.
# 
# # SELF-DESCRIPTION
# Your actions should be consistent with your self-description and personality.
# {description}
# 
# # RESPONSE METHOD
# Please perform actions by tool calling.
# """
        return system_content
