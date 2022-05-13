from slack_sdk.webhook import WebhookClient

from src.status import Status


class SlackMessage:
    def __init__(
        self,
    ):
        self.message = {}
        self.msg = None
        self.response_type = "in_channel"
        self.title = None
        self.title_link = None
        self.thumb_url = None
        self.text = None

    def get_message_from_video(
        self, status: Status, tiktok_object: dict = None, msg: str = None
    ) -> dict:
        if status == Status.failed:
            self.msg = msg
            return self.format_slack_message(status)
        else:
            video_id = tiktok_object.get("id")
            if video_id is None:
                video_id = tiktok_object["itemInfo"]["itemStruct"]["id"]
                title_link = tiktok_object["itemInfo"]["itemStruct"]["video"][
                    "playAddr"
                ]
                thumb_url = tiktok_object["itemInfo"]["itemStruct"]["video"]["cover"]
                text = tiktok_object["itemInfo"]["itemStruct"]["video"]["desc"]
            else:
                title_link = tiktok_object["play"]
                thumb_url = tiktok_object["cover"]
                text = tiktok_object["title"]

            self.msg = f"🔫 {video_id}: Ready pa fusilarlo"
            self.title = video_id
            self.title_link = title_link
            self.thumb_url = thumb_url
            self.text = text
        return self.format_slack_message(status)

    def format_slack_message(
        self,
        status: Status,
    ) -> str:
        self.message = {
            "response_type": self.response_type,
            "text": self.msg,
            "attachments": [],
        }

        attachment = {}
        attachment["author_name"] = "Fiebel"
        attachment["color"] = "#EA4435" if status == Status.failed else "#36A64F"
        attachment["title_link"] = self.title_link
        attachment["title"] = self.title
        attachment["text"] = self.text
        attachment["thumb_url"] = self.thumb_url

        self.message["attachments"].append(attachment)
        return self.message

    def webhook_send(self, webhook_url: str):
        webhook = WebhookClient(webhook_url)
        webhook.send(**self.message)
