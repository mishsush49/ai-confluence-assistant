import os
import sys
import time
import requests
from dotenv import load_dotenv
from atlassian import Confluence
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key='private',
)

def generate_content_from_openai(prompt_file_path):
    # Read the prompt from the file
    with open(prompt_file_path, 'r') as file:
        prompt = file.read().strip()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def publish_to_confluence(confluence_url, username, api_token, space_key, title, content, image_path):
    confluence = Confluence(
        url=confluence_url,
        username=username,
        password=api_token
    )

    # Check if the page already exists
    page_exists = confluence.page_exists(space=space_key, title=title)

    if page_exists:
        # Update the existing page
        page_id = confluence.get_page_id(space=space_key, title=title)
        confluence.update_page(
            page_id=page_id,
            title=title,
            body=content,
            parent_id=None,
            type='page',
            representation='storage'
        )
        print(f"Page '{title}' updated successfully.")
    else:
        # Create a new page
        page_id = confluence.create_page(
            space=space_key,
            title=title,
            body=content,
            parent_id=None,
            type='page',
            representation='storage'
        )
        page_id = confluence.get_page_id(space=space_key, title=title)
        
        print(f"Page '{title}' created with '{page_id}' successfully.")

    # Check if the image already exists as an attachment
    image_filename = os.path.basename(image_path)
    attachments = confluence.get_attachments_from_content(page_id)
    attachment_exists = any(attachment['title'] == image_filename for attachment in attachments['results'])

    if not attachment_exists:
        # Upload the image to the page using requests
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            upload_url = f"{confluence_url}/rest/api/content/{page_id}/child/attachment"
            headers = {
                'X-Atlassian-Token': 'no-check'
            }
            files = {
                'file': (image_filename, image_data, 'application/octet-stream')
            }
            response = requests.post(
                upload_url,
                headers=headers,
                auth=(username, api_token),
                files=files
            )
            response.raise_for_status()
            print(f"Image '{image_filename}' uploaded successfully.")
    else:
        print(f"Image '{image_filename}' already exists. Skipping upload.")

    # Wait for a short period to allow Confluence to process the image
    time.sleep(5)  # Adjust the delay as needed

    # Update the page content to include the image
    image_macro = f"""
    <ac:image>
        <ri:attachment ri:filename="{image_filename}" />
    </ac:image>
    """
    updated_content = content + image_macro
    confluence.update_page(
        page_id=page_id,
        title=title,
        body=updated_content,
        parent_id=None,
        type='page',
        representation='storage'
    )
    print(f"Page '{title}' updated with image successfully.")

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Read configuration from .env file
    confluence_url = os.getenv('CONFLUENCE_URL')
    username = os.getenv('CONFLUENCE_USERNAME')
    api_token = os.getenv('CONFLUENCE_API_TOKEN')
    space_key = os.getenv('CONFLUENCE_SPACE_KEY')
    
    # Check if the image path is provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Define the title of the Confluence page
    title = "Automated Confluence Page"

    # Generate content using OpenAI
    prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    content = generate_content_from_openai(prompt_file_path)

    # Publish the content to Confluence
    publish_to_confluence(confluence_url, username, api_token, space_key, title, content, image_path)

if __name__ == "__main__":
    main()