# Fiebel Video Service
![validate staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-pr.yaml/badge.svg)
![deploy staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-push.yaml/badge.svg?branch=main)

![Cloud infrastructure for the Fiebel Video Service](/static/infra_diagram.jpg)
Infrastructure to:
1. Slack bot to download media and metadata from Instagram
2. Slack bot to download media and metadata from TikTok
3. Trigger an encoding job to HSL
4. Host the video service via CDN

## Preparation
The terraform state is saved in `terraform.io`. Credentials for GCP must set up as follows:
1. Within the workspace create an environment variable `GOOGLE_CREDENTIALS`

### Set up Infrastructure and Functions
1. git clone
2. Setup a virtualenv (using `python -m venv .venv` or `pyenv virtualenv 3.8.12 fiebel`)
3. Activate a virtualenv (using `source .venv/bin/activate` or `pyenv activate fiebel`)
4. `make develop` to install any dev dependencies
5. #ship it

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


## TikTokAPI
This library needs `playwright` to work. In order to install it the Docker Image has been taken from [here](https://github.com/danofun/docker-playwright-python/blob/main/Dockerfile).