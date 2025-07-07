import sqlite3
import pandas as pd
import random

def generate_personas(data):
    """
    Uses the items from Oswald et al's (2025) survey and a collection 
    of int to str mappings (dicts) to recreate a seed user's submitted
    survey.
    This survey can then be used to imprint the seed persona onto the
    llm agent.

    Parameters
    data: .csv file containing the original user survey responses
    """

    # Dict that map survey responses to their respective str
    gender_dict = {
        1: "Male",
        2: "Female",
        3: "Other"
        }
    
    education_dict = {
        1: "Some high school or less (Grades 9-11 or Grade 12 with no diploma)",
        2: "High school graduate or GED (includes technical/vocational training that does not count towards college credit)",
        3: "Some college, no degree (includes some community college, associate's degree)",
        4: "Bachelor's degree (e.g., B.A. or B.S.)",
        5: "Some postgraduate or professional schooling, no postgraduate degree",
        6: "Postgraduate or professional degree (includes master's doctorate, medical or law degree)"
    }
    
    time_online_dict = {
        1: "no time at all",
        2: "up to one hour weekly",
        3: "up to one hour daily",
        4: "multiple hours daily",
        5: "almost the entire day"
    }
    
    social_media_dict = {
        1: "not at all",
        2: "a couple of times per week",
        3: "about once per day",
        4: "multiple times per day",
        5: "almost constantly"
    }
    
    comments_online_dict = {
        1: "never",
        2: "about once per month",
        3: "about once per week",
        4: "almost daily",
        5: "multiple times per day"
    }
    
    pol_interest_dict = {
        1: "Not interested at all",
        2: "Slightly interested",
        3: "Moderately interested",
        4: "Very interested"
    }
    
    issue_attitudes_dict = {
        1: "strongly disagree",
        2: "disagree",
        3: "rather disagree",
        4: "rather agree",
        5: "agree",
        6: "strongly agree"
    }
    
    issue_knowledge_dict = {
        1: "Nothing",
        2: "A little",
        3: "A moderate amount",
        4: "A lot"
    }
    
    political_efficacy_dict = {
        1: "strongly disagree",
        2: "disagree",
        3: "rather disagree",
        4: "rather agree",
        5: "agree",
        6: "strongly agree"
    }
    
    trust_general_dict = {
        1: "not at all",
        2: "not too much",
        3: "some",
        4: "a lot"
    }
    
    pol_cynicism_dict = {
        1: "Strongly disagree",
        2: "Somewhat disagree",
        3: "Neither agree nor disagree",
        4: "Somewhat agree",
        5: "Strongly agree"
    }

    # Template for an individual persona (passed to llm)
    persona_template = {
        "realname": None,
        "username": None,
        "bio": None,
        "persona": None,
        "age": None,
        "gender": None,
        "country": None,
      }

    # Empty list to hold individual personas
    seed_personas = []

    # Iterate over data and fill in seed user's survey responses
    for i, r in data.iterrows():
        try:
            pre_survey_questionnaire = (
                f"What is the highest level of school you have completed or the highest degree you have received? <{education_dict[r['education']]}>\n"
                # ---
                f"How much time do you spend online (browsing the web, using social media, etc.)? <{time_online_dict[r['time_online']]}>\n"
                f"How often do you use social media, including Reddit? <{social_media_dict[r['social_media']]}>\n"
                f"How often do you write comments online (on social media, in news outlets' comment sections, etc.)? <{comments_online_dict[r['comments_online']]}>\n"
                # ---
                f"In politics people often talk about the 'left' and the 'right'. On a scale between 1 (furthest left) and 11 (furthest right), where would you place yourself? (scale horizontal) <{r['leftright']}>\n"
                f"How interested in politics are you? <{pol_interest_dict[r['polinterest']]}>\n"
                f"How would you rate the Democratic Party? 0(negative) - 100(positive) <{r['affective_pol_1']}>\n"
                f"How would you rate the Republican Party? 0(negative) - 100(positive) <{r['affective_pol_2']}>\n"
                # ---
                f"How much do you agree with the following statements?\n"
                f"The government should not forgive student loan debt. <{issue_attitudes_dict[r['issue_attitudes_loan']]}>\n"
                f"Airbnb should be banned in cities. <{issue_attitudes_dict[r['issue_attitudes_airbnb']]}>\n"
                f"The federal minimum wage should be increased. <{issue_attitudes_dict[r['issue_attitudes_minwage']]}>\n"
                f"The US should provide financial and military aid to Ukraine. <{issue_attitudes_dict[r['issue_attitudes_ukraine']]}>\n"
                f"A universal basic income would kill the economy. <{issue_attitudes_dict[r['issue_attitudes_ubi']]}>\n"
                f"Climate change is one of the greatest threats to humanity. <{issue_attitudes_dict[r['issue_attitudes_climate']]}>\n"
                f"Fur clothing should be banned. <{issue_attitudes_dict[r['issue_attitudes_fur']]}>\n"
                f"The government should not invest in renewable energy. <{issue_attitudes_dict[r['issue_attitudes_renewable']]}>\n"
                f"The US should provide humanitarian aid to Gaza and call for ceasefire. <{issue_attitudes_dict[r['issue_attitudes_gaza']]}>\n"
                f"There should only be vegetarian food in cantines. <{issue_attitudes_dict[r['issue_attitudes_vegetarian']]}>\n"
                f"Things like gender-neutral language and stating pronouns are silly issues. <{issue_attitudes_dict[r['issue_attitudes_gender']]}>\n"
                f"Prostitution should be illegal. <{issue_attitudes_dict[r['issue_attitudes_sexwork']]}>\n"
                f"Employers should mandate vaccination. <{issue_attitudes_dict[r['issue_attitudes_vaccine']]}>\n"
                f"The government should not be responsible for providing universal health care. <{issue_attitudes_dict[r['issue_attitudes_healthcare']]}>\n"
                f"Immigrants should be mandated to adopt the local language and culture. <{issue_attitudes_dict[r['issue_attitudes_immigration']]}>\n"
                f"We need stricter gun control laws. <{issue_attitudes_dict[r['issue_attitudes_guns']]}>\n"
                f"The death penalty should be reestablished. <{issue_attitudes_dict[r['issue_attitudes_deathpenalty']]}>\n"
                f"Police officers should be wearing body cameras. <{issue_attitudes_dict[r['issue_attitudes_bodycams']]}>\n"
                f"Artificial Intelligence should replace humans where possible. <{issue_attitudes_dict[r['issue_attitudes_ai']]}>\n"
                f"Social media is a threat to democracy. <{issue_attitudes_dict[r['issue_attitudes_socialmedia']]}>\n"
                # ---
                f"How much do you know about the following issues?\n"
                f"Student Loan debt <{issue_knowledge_dict[r['issue_knowledge_loan']]}>\n"
                f"Airbnb <{issue_knowledge_dict[r['issue_knowledge_airbnb']]}>\n"
                f"Minimum wage <{issue_knowledge_dict[r['issue_knowledge_minwage']]}>\n"
                f"War in Ukraine <{issue_knowledge_dict[r['issue_knowledge_ukraine']]}>\n"
                f"Universal basic income <{issue_knowledge_dict[r['issue_knowledge_ubi']]}>\n"
                f"Climate change <{issue_knowledge_dict[r['issue_knowledge_climate']]}>\n"
                f"Fur clothing <{issue_knowledge_dict[r['issue_knowledge_fur']]}>\n"
                f"Renewable Energy <{issue_knowledge_dict[r['issue_knowledge_renewable']]}>\n"
                f"Middle East <{issue_knowledge_dict[r['issue_knowledge_mideast']]}>\n"
                f"Vegetarianism <{issue_knowledge_dict[r['issue_knowledge_vegetarian']]}>\n"
                f"Gender neutral language <{issue_knowledge_dict[r['issue_knowledge_gender']]}>\n"
                f"Prostitution <{issue_knowledge_dict[r['issue_knowledge_sexwork']]}>\n"
                f"Vaccine mandates <{issue_knowledge_dict[r['issue_knowledge_vaccine']]}>\n"
                f"Universal health care <{issue_knowledge_dict[r['issue_knowledge_healthcare']]}>\n"
                f"Assimilation <{issue_knowledge_dict[r['issue_knowledge_immigration']]}>\n"
                f"Gun control <{issue_knowledge_dict[r['issue_knowledge_guns']]}>\n"
                f"Death penalty <{issue_knowledge_dict[r['issue_knowledge_deathpenalty']]}>\n"
                f"Police body cameras <{issue_knowledge_dict[r['issue_knowledge_bodycams']]}>\n"
                f"Artificial Intelligence <{issue_knowledge_dict[r['issue_knowledge_ai']]}>\n"
                f"Social Media <{issue_knowledge_dict[r['issue_knowledge_socialmedia']]}>\n"
                # ---
                f"To what extent do you agree with the following statement?\n"
                f"I have a hard time understanding many political issues. <{political_efficacy_dict[r['political_efficacy_1']]}>\n"
                f"I know a great deal about politics. <{political_efficacy_dict[r['political_efficacy_2']]}>\n"
                f"I am very well informed about current political events. <{political_efficacy_dict[r['political_efficacy_3']]}>\n"
                # ---
                f"How much do you trust...\n"
                f"politics <{trust_general_dict[r['trust_general_1']]}>\n"
                f"media <{trust_general_dict[r['trust_general_2']]}\n"
                f"science <{trust_general_dict[r['trust_general_3']]}>\n"
                f"people generally <{trust_general_dict[r['trust_general_4']]}>\n"
                # ---
                f"To what extent do you agree with the following statement?\n"
                f"Quite a few of the people running the government are crooked. <{pol_cynicism_dict[r['pol_cynicism']]}>\n"
            )


            # Create seed user's persona
            persona = persona_template.copy()
            persona["realname"] = ""
            persona["username"] = r["ParticipantID"]
            persona["age"] = r["age"]
            persona["gender"] = gender_dict[r["gender"]]
            persona["bio"] = ""
            persona["persona"] = pre_survey_questionnaire
            persona["country"] = "US"
            seed_personas.append(persona)

        except:
            print("Missing Survey Info for user:", data.at[i, "ParticipantID"])

    # Return the list of seed personas
    return seed_personas