# Fiebel Video Service

![validate staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-pr.yaml/badge.svg)
![deploy staging](https://github.com/davidcava06/travelx-video-service/actions/workflows/main-push.yaml/badge.svg?branch=main)

![Cloud infrastructure for the Fiebel Video Service](/static/infra_diagram.jpg)
Infrastructure to:
1. Slack bot to download media and metadata from Instagram &#x2611;
2. Slack bot to download media and metadata from TikTok &#x2611;
3. Trigger an encoding job to HSL &#x2611;
4. Store media in IPFS via INFURA gateway &#x2611;
5. Like that, it can be callable for free via the `infura gateway`: https://PROJECT-ID.infura-ipfs.com/ipfs/CID &#x2611;


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


## CloudFlare Stream
This is a cheap CDN service provided by CloudFlare specifically for streamiing, information can be found [here](https://developers.cloudflare.com/stream/)

It is the service selected for MVP to host the media of the webapp due to the low cost and the functionalities such as:
- The Player API
- The Direct Creators Upload Link
- Security Features


### Player API
Code example:
```
<!DOCTYPE html>
<html>
  <head>
    <title>Hello World!</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
<!-- You can use styles and CSS on this iframe element where the video player will appear -->
<iframe
  src="https://iframe.videodelivery.net/21677bf7c76b4a53a5a11556b0beece6?preload=true&poster=https%3A%2F%2Fvideodelivery.net%2F21677bf7c76b4a53a5a11556b0beece6%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
  style="border: none"
  width="340"
  height="720"
  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
  allowfullscreen="true"
  id="stream-player"
></iframe>

<script src="https://embed.videodelivery.net/embed/sdk.latest.js"></script>

<!-- Your JavaScript code below-->
<script>
  const player = Stream(document.getElementById('stream-player'));
  player.addEventListener('play', () => {
    console.log('playing!');
  });
  player.play().catch(() => {
    console.log('playback failed, muting to try again');
    player.muted = true;
    player.play();
  });
</script>
  </body>
</html>
```


## Infura
Infrastructure provider for the Ethereum network and IPFS [here](https://infura.io).