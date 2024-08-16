import requests
from bs4 import BeautifulSoup

def fetch_website_body(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the body content
        body = soup.body
        
        if body:
            return body.get_text(separator="\n", strip=True)
        else:
            return "No body content found in the HTML."
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"