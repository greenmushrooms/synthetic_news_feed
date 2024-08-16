import openai
import json
from synthetic_news_feed.soup_parse import fetch_website_body
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt_api(text, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant that adds relevance grades to news articles."},
                {"role": "user", "content": text}
            ],
            max_tokens=2000,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred with the GPT API: {e}"

def enhance_story_dict(story_dict):
    try:
        # Convert the story_dict to a JSON string to send to GPT
        story_json = json.dumps(story_dict)
        prompt = f"Here is a JSON array of news articles. Please add a relevance grade (A to F) based on how relevant each article is to a data engineer. The JSON is:\n\n{story_json}"
        
        # Call GPT to enhance the story_dict with grades
        enhanced_story_json = call_gpt_api(prompt)
        
        # Convert the JSON string back to a dictionary
        try:
            enhanced_story_dict = json.loads(enhanced_story_json)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print("GPT response was:", enhanced_story_json)
            return {"error": "Failed to decode JSON"}

        return enhanced_story_dict
    except Exception as e:
        return {"error": str(e)}
    
def process_url(url):
    try:
        webpage_content = fetch_website_body(url)
        summary = call_gpt_api(f"Summarize the following text:\n\n{webpage_content}")
        detail = call_gpt_api(f"Clean up and provide detailed text for the following content:\n\n{webpage_content}")
        return {
            "summary": summary,
            "detail": detail
        }
    except Exception as e:
        return {"error": str(e)}
    
# Example usage:
if __name__ == "__main__":
    story_dict = {
        41247023: {"title": "SiFive announces high performance RISC-V cores for Datacentres"},
        41247024: {"title": "Show HN: If YouTube had actual channels"}
    }
    enhanced_story_dict = enhance_story_dict(story_dict)
    print(enhanced_story_dict)
