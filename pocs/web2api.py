import requests
import os
from bs4 import BeautifulSoup
import tempfile
from nodriver import Chrome
import time
from typing import List, Dict, Any
import argparse

def download_page(url: str) -> str:
    """Downloads the content of a web page and saves it to a temporary file.

    Args:
        url: The URL of the web page to download.

    Returns:
        The path to the temporary file containing the downloaded content.
    """
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request failed

    # Create a temporary file to store the downloaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
        temp_file.write(response.content)
        return temp_file.name

def extract_xhr_requests(temp_file_path: str) -> list:
    """Uses Nodriver to open the local HTML file in Chrome and extract XHR requests.

    Args:
        temp_file_path: The path to the temporary HTML file.

    Returns:
        A list of dictionaries containing information about each XHR request.
    """
    with Chrome(headless=True) as browser:
        browser.get(f"file://{temp_file_path}")
        # Wait for the page to be ready for interactions
        browser.wait_for_page_load()  # Use nodriver's wait_for_page_load method
        # Access Chrome DevTools objects to get XHR requests
        network_log = browser.get_network_log()
        xhr_requests = []
        for entry in network_log:
            if entry['type'] == 'XHR':
                xhr_requests.append({
                    "url": entry['request']['url'],
                    "method": entry['request']['method'],
                    "request_headers": entry['request']['headers'],
                    "request_body": entry['request']['postData'],
                    "response_headers": entry['response']['headers'],
                    "response_body": entry['response']['body']
                })
        return xhr_requests

def generate_pydantic_models(xhr_requests: List[Dict[Any, Any]]) -> str:
    """Generates Pydantic models from XHR requests using Gemini.

    Args:
        xhr_requests: A list of dictionaries containing information about each XHR request.

    Returns:
        A string containing the generated Pydantic models.
    """
    pydantic_models = []
    for request in xhr_requests:
        # Construct a prompt for Gemini based on the request and response data
        prompt = f"""
        Generate Pydantic models for the following API endpoint:
        URL: {request['url']}
        Method: {request['method']}
        Request Headers: {request['request_headers']}
        Request Body: {request['request_body']}
        Response Headers: {request['response_headers']}
        Response Body: {request['response_body']}

        Include sample invocation code for the API.
        """

        # Use Gemini to generate the Pydantic models and sample invocation
        # ... (Implementation using Gemini API)

        # Example output:
        # pydantic_models.append(f"""
        # from pydantic import BaseModel
        # 
        # class RequestModel(BaseModel):
        #     # ... fields based on request body
        # 
        # class ResponseModel(BaseModel):
        #     # ... fields based on response body
        # 
        # # Sample invocation
        # response = requests.post(
        #     "https://api.example.com/data",
        #     json=RequestModel(
        #         # ... values based on request body
        #     ).dict()
        # )
        # response_data = ResponseModel.parse_obj(response.json())
        # """)

    return "\n".join(pydantic_models)

def main():
    parser = argparse.ArgumentParser(description="Generate Pydantic models from a web page's XHR requests.")
    parser.add_argument("url", help="The URL of the web page to analyze.")
    args = parser.parse_args()

    temp_file_path = download_page(args.url)
    xhr_requests = extract_xhr_requests(temp_file_path)
    pydantic_code = generate_pydantic_models(xhr_requests)

    # Save the generated Pydantic models to a file
    with open("generated_models.py", "w") as f:
        f.write(pydantic_code)

if __name__ == "__main__":
    main()
