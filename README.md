# Fiebel Video Service

![validate staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-pr.yaml/badge.svg)
![deploy staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-push.yaml/badge.svg?branch=main)

![Cloud infrastructure for the Fiebel Video Service](/static/infra_diagram.jpg)
Infrastructure to:
1. Slack bot to download media and metadata from Instagram &#x2611;
2. Slack bot to download media and metadata from TikTok &#x2611;
3. Trigger an encoding job to HSL &#x2611;
4. Store media in IPFS via INFURA gateway
5. Like that, it can be callable for free via the `cloudflare gateway`: https://cloudflare-ipfs.com/ipfs/CID


## Preparation
The terraform state is saved in `terraform.io`. Credentials for GCP must set up as follows:
1. Within the workspace create an environment variable `GOOGLE_CREDENTIALS`


### Set up Infrastructure and Functions
1. git clone
2. Setup a virtualenv (using `python -m venv .venv` or `pyenv virtualenv 3.8.12 fiebel`)
3. Activate a virtualenv (using `source .venv/bin/activate` or `pyenv activate fiebel`)
4. `make develop` to install any dev dependencies
5. #ship it

Call Pub/Sub event driven functions:
`DATA=$(printf 'Hello!'|base64) && gcloud functions call hello_pubsub --data '{"data":"'$DATA'"}'`


### Set up TikTok API
1. git clone
2. `cd apps/tiktok-api`
3. Setup a virtualenv (using `python -m venv .venv` or `pyenv virtualenv 3.8.12 tiktok_api`)
4. Activate a virtualenv (using `source .venv/bin/activate` or `pyenv activate tiktok_api`)
5. `make develop` to install any dev dependencies
6. `python -m playwright install`
7. #ship it

8. `docker build . -t tiktok`
9. `docker run -it -p 8000:8080 tiktok`


### [TMP] Call Transcoder Cloud Function
To the Cloud Function endpoint, send a payload like this:
```
event = {
    "attributes": {
        "response_url": "https://hooks.slack.com/services/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"
    },
    "data": "dGlrdG9rLzcwODE3MjMzNjM1NDYxODkwNjEvdmlkZW8ubXA0,
}
```

You can get the `base64` encoded string doing this:
`echo -n 'tiktok/7082326632828062982/video.mp4' | base64`


## TikTokAPI
This library needs `playwright` to work. In order to install it the Docker Image has been taken from [here](https://github.com/danofun/docker-playwright-python/blob/main/Dockerfile).