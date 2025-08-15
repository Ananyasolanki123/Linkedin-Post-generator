from llm_helper import llm
from fewshots import FewShotPosts
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

few_shot = FewShotPosts()

def get_length_str(length):
    mapping = {
        "Short": "1 to 5 lines",
        "Medium": "6 to 10 lines",
        "Long": "11 to 15 lines"
    }
    return mapping.get(length, "6 to 10 lines")


def generate_post_from_sheet(row):
    """Generates LinkedIn post from a form row."""
    length = row.get("Length", "Medium")
    language = row.get("Language", "English")
    tag = row.get("Keyword/Tags", "") or row.get("Keyword/Tags_2", "")

    location = row.get("Company Location", "") or row.get("Location", "") or "N/A"
    office = row.get("Office", "") or row.get("Company Name", "") or "N/A"

    user_topic = (
        row.get("Describe your project, achievement, campaign, or announcement", "")
        or row.get("Describe your project, achievement, campaign, or announcement_2", "")
    )
    caption = row.get("Caption", "")
    tone = row.get("Select Tone", "") or row.get("Select Post Tone_2", "")

    # === NewsAPI facts ===
    news_facts = []
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if NEWS_API_KEY:
        query = f"{tag} {user_topic}".strip()
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=3&apiKey={NEWS_API_KEY}"
        try:
            articles = requests.get(url).json().get("articles", [])
            for art in articles:
                news_facts.append({
                    "title": art.get("title", ""),
                    "source": art.get("source", {}).get("name", ""),
                    "published": art.get("publishedAt", "")[:10],
                    "description": art.get("description", "")
                })
        except Exception as e:
            print(f"[WARN] Failed to fetch news: {e}")

    project_info = f"""
    Topic: {tag}
    Location: {location}
    Office: {office}
    Description: {user_topic}
    Caption: {caption}
    Tone: {tone}
    """

    if news_facts:
        prompt = get_prompt_with_news(project_info, news_facts, tone, include_sources=True)
    else:
        prompt = get_prompt(length, language, tag, location, office, user_topic, caption, tone, "")

    return llm.invoke(prompt).content


def get_prompt_with_news(project_info, news_facts, tone, include_sources=False):
    news_text = "\n".join(
        f"- {fact['description']} (Source: {fact['source']}, {fact['published']})"
        for fact in news_facts if fact["description"]
    )

    prompt = f"""
    Write a LinkedIn post of approximately 100 words.
    The post should:
    - Explain the project based on the following info within 100 word: {project_info}
    - Naturally highlight the caption **{project_info.split("Caption:")[1].strip()}** (make it stand out with bold formatting).
    - Include the recent industry facts below, but limit them to about 40 words total:
      {news_text}
    - Maintain the tone: {tone}.
    - Do not include phrases like "Here is your LinkedIn post" or mention the word count.
    - Make it ready-to-post text only, without any meta instructions.
    { 'At the end, list the sources in parentheses.' if include_sources else '' }
    """

    return prompt



def generate_analytics_feedback(impressions, reactions, comments, shares):
    engagement_rate = ((reactions + comments + shares) / impressions * 100) if impressions else 0
    feedback_prompt = f"""
    You are a LinkedIn post coach. Analyze these post analytics and give 3 short, actionable tips for improvement.
    
    Impressions: {impressions}
    Reactions: {reactions}
    Comments: {comments}
    Shares: {shares}
    Engagement Rate: {engagement_rate:.2f}%

    Keep feedback under 20 words and easy for a beginner to follow.
    """
    return llm.invoke(feedback_prompt).content


def get_prompt(length, language, tag, location, office, user_topic, caption, tone, news_section):
    length_str = get_length_str(length)
    prompt = f"""
    Generate a LinkedIn post using the following details. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language} (If Hinglish, write in English script)
    4) Location: {location}
    5) Office/Organization: {office}
    6) Description: {user_topic}
    7) Caption: {caption}
    8) Tone: {tone}
    9) Relevant recent news & facts:
    {news_section}

    The tone should be {tone} yet engaging. Ready to post on LinkedIn without hashtags.
    """
    examples = few_shot.get_filtered_posts(length, language, tag)
    if examples:
        prompt += "\n\nExample posts:\n"
        for i, post in enumerate(examples[:2]):
            prompt += f"\nExample {i+1}:\n{post['text']}\n"
    return prompt


def safe_int(value):
    """Safely convert value to int, returning 0 if not possible."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
