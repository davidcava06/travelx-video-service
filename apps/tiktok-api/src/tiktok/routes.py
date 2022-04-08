from src import http, logging
from starlette.requests import Request
from starlette.routing import Route

# from TikTokApi import TikTokApi


log = logging.get_logger(__name__)


async def get_video(request: Request):
    """Get Video from TikTok
    ---
    description: Given a TikTok URL, return the video
    responses:
        200:
            description: Executes request
        400:
            description: Bad Request
        403:
            description: Forbidden
    """
    # with TikTokApi() as api:
    #     video = api.video(id="7068273969094200582")
    #     breakpoint()
    #     # Bytes of the TikTok video
    #     video_data = video.bytes()

    #     with open("out.mp4", "wb") as out_file:
    #         out_file.write(video_data)
    return http.APIResponse(content={"status": "It's coming..."}, status_code=200)


routes = [Route("/", get_video, methods=["GET"])]
