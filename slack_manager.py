import logging
import re
import time
from typing import Generator

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_HISTORY_SIZE = 100


class SlackManager:
    """
    Class that provides some functionalities around Slack WebClient
    """

    def __init__(self):
        self._token = None
        self._client = None

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value
        self._client = WebClient(token=self._token)

    @property
    def client(self) -> WebClient:
        return self._client

    def post_file(self, token: str, channel: str, content: str, filename: str) -> None:
        """
        Post a file on a given slack channel

        :param token: access token to slack workspace
        :param channel: channel where to post the file
        :param content: file content
        :param filename: name of the file
        """
        self.token = token
        try:
            self.client.files_upload(
                channels=channel,
                content=content,
                filename=filename,
                filetype="csv",
            )
        except SlackApiError as e:
            logging.error(
                f"post_file: failed for channel {channel} with the following error \n{e}"
            )

    def channel_history_iter(
        self,
        token: str,
        channel: str,
        oldest: int = 0,
        latest: int = 0,
        cursor: str = None,
    ) -> Generator[str, None, None]:
        """
        Provides an iterator that goes through a slack channel's history

        :param token: access token to slack workspace
        :param channel: channel we want to fetch history from

        :optional oldest: timestamp of the oldest message
        :optional latest: timestamp of the latest message
        :option cursor: starting point of the iteration

        :yields message: next history message
        """
        if not latest:
            latest = time.time()

        self.token = token
        try:
            response = self.client.conversations_history(
                channel=channel,
                limit=SLACK_HISTORY_SIZE,
                cursor=cursor,
            ).data
        except SlackApiError as e:
            logging.error(
                f"channel_history_iter: INIT failed for channel {channel} with the following error \n{e}"
            )
            return
        while True:
            for message in response["messages"]:
                if float(message["ts"]) > latest or float(message["ts"]) < oldest:
                    return

                yield message

            cursor = response.get("response_metadata", {}).get("next_cursor", "")
            if not cursor:
                return

            try:
                response = self.client.conversations_history(
                    channel=channel,
                    limit=SLACK_HISTORY_SIZE,
                    cursor=cursor,
                ).data
            except SlackApiError as e:
                logging.error(
                    f"channel_history_iter: NEXT failed for channel {channel} with the following error \n{e}\nNext cursor : {cursor}"
                )
                return
        return