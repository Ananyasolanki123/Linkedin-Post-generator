import unicodedata
import re
import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

# --- Text cleaning helper ---
def clean_text(text: str) -> str:
    """Remove invalid surrogate characters and normalize text."""
    text = re.sub(r'[\ud800-\udfff]', '', text)  # Remove unpaired surrogates
    return unicodedata.normalize("NFKC", text)

def clean_json_output(text: str) -> str:
    """Remove markdown fences and comments from JSON output."""
    text = re.sub(r"```(?:json)?", "", text)
    text = re.sub(r"//.*", "", text)
    return text.strip()

def extract_metadata(post_text: str) -> dict:
    """Extract metadata like line count, language, and tags from text."""
    template = '''
You are given a LinkedIn post. Extract number of lines, language, and tags.
1. Output valid JSON only, with keys: line_count, language, tags.
2. tags is an array with max two tags.
3. Language should be English or Hinglish.
Post:
{post}
'''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post_text})

    try:
        json_parser = JsonOutputParser()
        raw_output = clean_json_output(response.content)
        result = json_parser.parse(raw_output)
    except OutputParserException as e:
        raise OutputParserException("Unable to parse metadata JSON.") from e

    result['tags'] = [clean_text(tag) for tag in result.get('tags', [])]
    return result

def process_posts(raw_file_path="Data/raw_posts.json", processed_file_path="Data/processed_posts.json"):
    """Batch process posts from JSON file."""
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)

    enriched_posts = []
    for post in posts:
        metadata = extract_metadata(clean_text(post['text']))
        enriched_posts.append({**post, **metadata})

    with open(processed_file_path, "w", encoding='utf-8') as outfile:
        json.dump(enriched_posts, outfile, indent=4, ensure_ascii=False)

def process_single_post(caption_text: str) -> dict:
    """Process a single WhatsApp caption directly."""
    caption_text = clean_text(caption_text)
    return extract_metadata(caption_text)

if __name__ == '__main__':
    # For batch mode:
    process_posts()
    # For single WhatsApp caption test:
    # print(process_single_post("Women's internship closing ceremony at RUIDP Jaipur."))
