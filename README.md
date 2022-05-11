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


### [TMP] Experience Object for testing
```
experience_object = {'uid': 'd90b9599-9b55-41fb-84d3-69f4e476e4c5', 'parent': None, 'languages': {'primary': 'English', 'secondary_languages': None}, 'title': None, 'description': None, 'external_url': None, 'status': 'pending', 'category': 'activity', 'audience': None, 'hashtags': None, 'at_guest_location_ind': False, 'location': {'address': None, 'category': '', 'city': None, 'country': None, 'lat': 51.541, 'lng': -0.1433, 'name': 'Camden Town', 'phone': '', 'website': '', 'zip': None, 'description': None, 'instructions': None}, 'media': [{'storage': 'cloudflare', 'uid': 'ea3e3332-00d0-4ea1-aaf2-5c176953cc66', 'name': 'CdVQBTyIFLo', 'hls': 'https://videodelivery.net/1be02fc9d30645449b53f0131911284f/manifest/video.m3u8', 'dash': 'https://videodelivery.net/1be02fc9d30645449b53f0131911284f/manifest/video.mpd', 'storage_id': '1be02fc9d30645449b53f0131911284f', 'size': 3332486, 'thumbnail': 'https://videodelivery.net/1be02fc9d30645449b53f0131911284f/thumbnails/thumbnail.jpg', 'created_at': '2022-05-11T14:47:31.535038Z', 'uploaded_at': '2022-05-11T14:47:31.535032Z'}], 'author': {'username': 'its_so_london', 'provider': 'instagram', 'display_name': 'London UK 🇬🇧', 'avatar_url': None}, 'is_free': True, 'is_eco': False, 'eco_features': None, 'duration_hours': None, 'group_size': {'default_public_max_size': None, 'default_private_max_size': None}, 'guest_requirements': {'min_age': None, 'infant_can_attend': False, 'verified_id_ind': False, 'other_requirements': None, 'activity_level': 'light', 'skill_level': 'beginner'}, 'pricing': {'price': {'currency': 'GBP', 'value': 0, 'unit': 'guest'}, 'price_per_infant': None, 'minimum_private_booking_price': None, 'caregiver_free_ind': False, 'security_deposit': None, 'discounts': None}, 'amenities': {'included_amenities': None, 'extra_amenities': None, 'packing_items': None}, 'booking_settings': {'default_confirmed_booking_lead_hours': None, 'default_booking_lead_hours': None, 'max_hours': None, 'restricted_start_days': None, 'default_private_booking_ind': False, 'cancellation_policy': 'forbidden', 'rules': None, 'instant_book_ind': False, 'contact_host_ind': True, 'check_in': {'default_time': None, 'default_min_time': None, 'default_max_time': None, 'window_days': None, 'instructions': None}, 'check_out': {'default_time': None, 'default_min_time': None, 'default_max_time': None, 'window_days': None, 'instructions': None}}}
```

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