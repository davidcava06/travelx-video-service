# Fiebel Video Service
![validate staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-pr.yaml/badge.svg?branch=main)
![deploy staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-push.yaml/badge.svg)

![Cloud infrastructure for the Fiebel Video Service](/static/infra_diagram.jpg)
Infrastructure to:
1. Upload raw video to Cloud Storage
2. Trigger an encoding job to HSL
3. Host the video service via CDN

## Preparation
The terraform state is saved in `terraform.io`. Credentials for GCP must set up as follows:
1. Within the workspace create an environment variable `GOOGLE_CREDENTIALS`
2. Make it the value of the key for the employed service account with no new lines.
3. In order to use Cloud Scheduler initialising an App Engine app is needed.

4. git clone
5. Setup a virtualenv (using `python -m venv .venv` or `pyenv virtualenv 3.7.9 investment-cloud`)
6. Activate a virtualenv (using `source .venv/bin/activate` or `pyenv activate investment-cloud`)
7. `make develop` to install any dev dependencies
8. #ship it


## TikTokAPI
This library needs `playwright` to work. In order to install it the Docker Image has been taken from [here](https://github.com/danofun/docker-playwright-python/blob/main/Dockerfile).