from openai import OpenAI
import json
import pandas as pd
from tqdm import tqdm
import re

persona_data = []

for i in [1, 6]:
    with open(f"/../abyss/home/oasis/oasis-rutschmanna/data/reddit/seed_personas_subreddit_{i}.json", "r") as f:
        persona_data.extend(json.load(f))

persona_data_df = pd.DataFrame(persona_data).drop(columns="bio")
seed_user_ids = persona_data_df["username"]
persona_data_df.set_index("username", inplace=True)

sys_prompt = """
You are a Reddit user. The following survey contains several questions and your answers. The answers are contained between '<' and '>', eg. question: 'How much time do you spend online (browsing the web, using social media, etc.)?', answer: '<multiple hours daily>'. This survey constitutes your persona.
This is your survey:

{}

You will be shown a post from the social media platform Reddit.
Your task is to read the post and then give an answer on whether you would like to participate in the discussion related to the given post. Decide only based on what would be most in line with your persona. On Reddit users are faced with a multitude of different conversations to take part in. Since time is limited, they usually cannot contribute to every conversation and have to decide whether the conversation is important enough to spend time on.

Please answer by giving a yes or no reply to the question "Would it be in line with your persona to participate in this conversation?". Only answer with 'yes' or 'no'.

You are not supposed to be helpful or over eager to join the conversation.
Only answer with 'yes' if you really feel that it would be in line with your persona. Otherwise, answer with 'no'.
Please consider the following post:
"""

user_prompt = """
{}
"""

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

agent_responses = []
agent_responses_bool = []
prompt_topics = []

def main():
    client = OpenAI(
        api_key="EMPTY",
        base_url="http://127.0.0.1:8002/v1",
    )

    for i in tqdm(seed_user_ids):
        for j in list(topics.keys()):
            completion = client.chat.completions.create(
                model="qwen",
                messages=[
                    {"role": "system", "content": sys_prompt.format(persona_data_df.at[i, "persona"])},
                    {"role": "user", "content": user_prompt.format(topics[j])},
                ],
            )

            prompt_topics.append(j)
            agent_responses.append(completion.choices[0].message.content)
            agent_responses_bool.extend(re.findall(r"(?<=<\/think>)\s*(yes|no)", completion.choices[0].message.content))

    print(len(prompt_topics))
    print(len(agent_responses))
    print(len(list(seed_user_ids)*20))
    
    try:
        pd.DataFrame(
            {"seed_user_id": list(seed_user_ids)*20,
             "topic": prompt_topics,
             "joined": agent_responses_bool,
             "reason": agent_responses}
        ).to_csv("join_reasoning.csv", index=False)
    
    except:
        try:
            pd.DataFrame(
                {"joined": agent_responses_bool,
                 "reason": agent_responses}
            ).to_csv("bool_only_join_reasoning.csv", index=False)
        
        except:
            pd.DataFrame(
                {"reason": agent_responses}
            ).to_csv("reason_only_join_reasoning.csv", index=False)   

if __name__ == "__main__":
    main()