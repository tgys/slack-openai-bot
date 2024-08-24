## README.md

### Usage example

replace the empty strings in the variables 
SLACK_CLIENT_ID = ""
SLACK_CLIENT_SECRET = ""
SLACK_SIGNING_SECRET = ""
OPENAI_API_KEY = ""
with the keys from the slack api tab

<div style="display: flex; align-items:flex-start; object-fit:scale-down; " class="single-photo-box">
        <img id="p2_i_1" src="https://api.piwibox.me/images/making_an_openai_slack_bot_in_python/1.png" width="550"></img>
</div>
</div>

replace the bot_token variable in handle_message_events with the token from the install app tab
<div style="display: flex; align-items:flex-start; object-fit:scale-down; " class="single-photo-box">
        <img id="p2_i_2" src="https://api.piwibox.me/images/making_an_openai_slack_bot_in_python/2.png" width="500"></img>
</div>
</div>

goto the Oauth and Permissions tab and make sure it has the following scopes
<div style="display: flex; align-items:flex-start; object-fit:scale-down; " class="single-photo-box">
        <img id="p2_i_3" src="https://api.piwibox.me/images/making_an_openai_slack_bot_in_python/3.png" width="450"></img>
</div>
</div>

replace OPENAI_API_KEY with the secret key from the openai api settings
<div style="display: flex; align-items:flex-start; object-fit:scale-down; " class="single-photo-box">
        <img id="p2_i_4" src="https://api.piwibox.me/images/making_an_openai_slack_bot_in_python/4.png" width="500"></img>
</div>
</div>

#### running it with docker/podman

run `sudo podman build -t slackbot .` (or use docker instead of podman) to build the image and then
`sudo podman run -it --rm slackbot` to run the container

#### running it with nix-shell
there's also a nix shell file that installs all the dependencies

#### expected output

you should be able to upload images and gifs and get a response from openai
<div style="display: flex; align-items:flex-start; object-fit:scale-down; " class="single-photo-box">
        <img id="p2_i_5" src="https://api.piwibox.me/images/making_an_openai_slack_bot_in_python/6.png" width="350"></img>
</div>
</div>

