from synthetic_news_feed.soup_parse import fetch_website_body
import requests
import os
from synthetic_news_feed.agent_calls import process_url, enhance_story_dict

# Function to fetch top story IDs from Hacker News
def get_hy_top_story_ids(limit=10):
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        response.raise_for_status()
        top_stories = response.json()
        return top_stories[:limit]
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Function to fetch story details from Hacker News
def get_story_headers(story_array):
    story_dict = {}
    for item in story_array:
        try:
            url = f"https://hacker-news.firebaseio.com/v0/item/{item}.json"
            response = requests.get(url)
            response.raise_for_status()
            story_data = response.json()
            story_dict[item] = {
                "by": story_data.get("by", ""),
                "descendants": story_data.get("descendants", 0),
                "id": story_data.get("id", 0),
                "kids": story_data.get("kids", []),
                "score": story_data.get("score", 0),
                "time": story_data.get("time", 0),
                "title": story_data.get("title", ""),
                "type": story_data.get("type", ""),
                "url": story_data.get("url", ""),
            }
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching story {item}: {e}")
    
    return story_dict

# Function to display stories for selection and return the selected story
def select_story(title_id_array):
    print("Select a news story:")
    for idx, (title, id_, grade) in enumerate(title_id_array, 1):
        print(f"{idx}. ID: {id_} | Title: {title} | Relevance Grade: {grade}")
    
    selected_idx = int(input("\nEnter the number of the story you want to select: ")) - 1
    return title_id_array[selected_idx]

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to display summary and prompt for details
def display_summary_and_prompt(story_title, summary, detail):
    clear_screen()
    print(f"Title: {story_title}\n")
    
    # Print the summary only
    json_output = {
        "summary": summary,
        "detail": detail
    }
    
    print(f"Summary: {json_output['summary']}\n")
    
    # Ask if the user wants to view the details
    show_detail = input("Would you like to view the details? (y/n): ").strip().lower()
    
    if show_detail == 'y':
        clear_screen()
        print(f"Details for: {story_title}\n")
        print(f"{json_output['detail']}\n")
        input("Press Enter to go back to the main menu...")


def merge_story_dicts(original_dict, enhanced_dict):
    merged_dict = {}
    # Convert keys of enhanced_dict to integers
    enhanced_dict = {int(key): value for key, value in enhanced_dict.items()}
    
    for key, value in original_dict.items():
        if key in enhanced_dict:
            merged_dict[key] = value
            merged_dict[key]['relevance_grade'] = enhanced_dict[key]
        else:
            merged_dict[key] = value
            merged_dict[key]['relevance_grade'] = 'No grade'
    return merged_dict
    
def main():
    story_array = get_hy_top_story_ids(5)
    story_dict = get_story_headers(story_array)
    enhanced_story_dict = enhance_story_dict(story_dict)

    # Merge original story data with the relevance grades
    merged_story_dict = merge_story_dicts(story_dict, enhanced_story_dict)
    
    # Prepare array with titles, ids, and grades
    title_id_array = [
        [story['title'], story['id'], story.get('relevance_grade', 'No grade')]
        for story in merged_story_dict.values()
    ]

    while True:
        selected_story = select_story(title_id_array)
        story_title = selected_story[0]
        story_id = selected_story[1]
        story_url = merged_story_dict[story_id]['url']

        if story_url:
            content = process_url(story_url)
            summary = content.get("summary", "No summary available")
            detail = content.get("detail", "No detail available")
            
            # Display summary and offer to show details
            display_summary_and_prompt(story_title, summary, detail)
        else:
            print("No URL available for this story.")

if __name__ == "__main__":
    main()
