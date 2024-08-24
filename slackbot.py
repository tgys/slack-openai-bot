import os
import openai
import base64
import requests
import cv2  
import time
import mimetypes
from openai import OpenAI
from flask import Flask, request, redirect
from slack_sdk import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.signature import SignatureVerifier

# Set your credentials
SLACK_CLIENT_ID = ""
SLACK_CLIENT_SECRET = ""
SLACK_SIGNING_SECRET = ""
OPENAI_API_KEY = ""

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize installation store and state store
installation_store = FileInstallationStore(base_dir="./data/installations")
state_store = FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")

# Slack OAuth setup
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=SLACK_CLIENT_ID,
    scopes=["channels:read", "channels:join", "groups:read", "chat:write", "app_mentions:read", "files:write", "files:read", "channels:history"],
    redirect_uri="http://localhost:5250/slack/oauth_redirect"
)


# Slack WebClient
client = WebClient()
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# Store the last 100 messages
message_history = []

def check_file(file_path):
    if os.path.exists(file_path):
        print(f"The file '{file_path}' exists.")
        file_type, _ = mimetypes.guess_type(file_path)
        if file_type:
            print(f"The file type is: {file_type}")
        else:
            print("Could not determine the file type.")
    else:
        print(f"The file '{file_path}' does not exist.")

# OAuth install route
@app.route("/slack/install", methods=["GET"])
def install():
    state = state_store.issue()
    url = authorize_url_generator.generate(state)
    return redirect(url)

# OAuth redirect route
@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    if "code" in request.args:
        code = request.args["code"]
        state = request.args["state"]
        
        if not state_store.consume(state):
            return "Invalid state parameter", 400

        response = client.oauth_v2_access(
            client_id=SLACK_CLIENT_ID,
            client_secret=SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri="http://localhost:5250/slack/oauth_redirect"
        )

        if response["ok"]:
            installation_store.save(response)
            print("Installation successful!")
            return "Installation successful!"
        else:
            print("OAuth failed")
            return "OAuth failed", 400


@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Verify the request signature
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        print("Invalid signature")
        return "Invalid signature", 400


    # Check if X-Slack-Retry-Num header exists and is greater than 1
    retry_num = request.headers.get('X-Slack-Retry-Num')
    print(f"\n\nRETRY NUMBER {retry_num}\n\n")
    
    if retry_num is not None and int(retry_num) >= 1:
        print(f"Ignoring event due to retry number {retry_num}")
        return "", 200  # Acknowledge the event without processing

    # Get the headers from the request
    headers = request.headers

    # Get the value of the 'token' field from the headers
    ## token_value = headers.get('token')
    ## print(f"Token value from headers: {token_value}")

    body = request.json
    print(f"Received event: {body}")  # Debug: Print the entire event payload
    
    if "challenge" in body:
        print("Responding to Slack challenge")
        return body["challenge"]
    
    if body["event"]["type"] == "app_mention":
        print(f"App mention detected: {body['event']['text']}")  # Debug: Print the mention text
        handle_message_events(body)
    
    return "", 200


def convert_image_to_jpeg(image_path):
    try:
        # Read the image using OpenCV
        time.sleep(5)

        check_file(image_path)

        img = cv2.imread(image_path)
        print("image path is ")
        print(image_path)
        if img is None:
            raise ValueError("Could not read the image file")

        # Convert the image to RGB if necessary (OpenCV loads images in BGR format)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Save the image as JPEG
        jpeg_path = image_path.rsplit(".", 1)[0] + ".jpg"
        cv2.imwrite(jpeg_path, img_rgb)
        return jpeg_path
    except Exception as e:
        print(f"Error converting image to JPEG: {e}")
        raise



def download_image(image_url, hdrs):
    ## response = requests.get(image_url, headers=hdrs)
    ## if response.status_code == 200:

        local_filename = image_url.split("/")[-1]
        

        with open(local_filename, 'wb') as f:
            r = requests.get(image_url, stream=True, headers=hdrs)
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


        print(f"Downloaded image size: {os.path.getsize(local_filename)} bytes")
        return local_filename



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def handle_message_events(body):
    global message_history
    team_id = body["team_id"]

    bot_token = ""
    
    # Create a WebClient with the bot token
    webclient = WebClient(token=bot_token)

    # Extract the text after the mention
    user_id = body["event"]["user"]
    message_text = str(body["event"]["text"]).strip()
    print(f"Message text: {message_text}")  # Debug: Print the extracted message text

    # Add the new message to the history
    message_history.append({"role": "user", "content": message_text})
    
    # Trim the history to the last 100 messages
    if len(message_history) > 100:
        message_history = message_history[-100:]

    # Initialize OpenAI API
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Check if there are any images in the event
    if "files" in body["event"]:
        for file_info in body["event"]["files"]:
            if file_info["mimetype"].startswith("image/"):
                # Download the image from Slack
                local_image_path = download_image(file_info["url_private_download"], hdrs={"Authorization": f"Bearer {bot_token}"})
                if local_image_path:
                    current_directory = os.getcwd()
                    abs_file_path = os.path.join(current_directory, local_image_path)
                    
                    # Encode the image (GIF or otherwise)
                    encoded_image = encode_image(abs_file_path)
                    
                    # Determine the MIME type
                    ftype = file_info["mimetype"]

                    # Add the encoded image to the message payload
                    message_history.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "What’s in this image?"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{ftype};base64,{encoded_image}"
                                    }
                                }
                            ]
                        }
                    )
                    # Optionally, clean up the local files
                    os.remove(abs_file_path)

    elif "attachments" in body["event"]:
        print("found attachment in event")
        for attachment in body["event"]["attachments"]:
            if "image_url" in attachment["blocks"][0]:
                print("found image url in attachment")
                image_url = attachment["blocks"][0]["image_url"]
                # Download the GIF or image
                local_image_path = download_image(image_url, hdrs={"Authorization": f"Bearer {bot_token}"})
                print("downloaded gif")
                print(local_image_path)
                if local_image_path:
                    encoded_image = encode_image(local_image_path)
                    
                    # MIME type for GIFs is typically image/gif
                    ftype = "image/gif"

                    # Add the encoded GIF to the message payload
                    message_history.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "What’s in this GIF?"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{ftype};base64,{encoded_image}"
                                    }
                                }
                            ]
                        }
                    )
                    # Optionally, clean up the local files
                    os.remove(local_image_path)

    print("before openai completion call")

    response = client.chat.completions.create(
        messages=message_history,
        model="gpt-4-turbo",
        stream=False  # Disable streaming
    )
    
    # Extract the content from the response directly
    buffered_content = response.choices[0].message.content
    
    print("buffered content: ")
    print(buffered_content)
    
    if buffered_content:
        webclient.chat_postMessage(
            channel=body["event"]["channel"],
            text=buffered_content
        )


if __name__ == "__main__":
    print("Starting the Flask app...")
    app.run(host="0.0.0.0", port=5250)
