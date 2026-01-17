import os
import re
import logging
from pathlib import Path
from datetime import datetime, timezone

from atproto import Client, models

logger = logging.getLogger(__name__)


def _is_valid_username(s: str) -> bool:
    pattern = re.compile(r'^[a-zA-Z0-9_]{4,25}$')
    return bool(pattern.fullmatch(s))


def _prepare_client():
    if not hasattr(_prepare_client, "_client"):
        _prepare_client._client = Client()
    login_info = [os.getenv('BSKY_USER_NAME'), os.getenv('BSKY_PASSWORD')]
    if ~all(login_info):
        logger.error("BSKY_USER_NAME os BSKY_PASSWORD is not set.")
        raise ValueError("BSKY_USER_NAME os BSKY_PASSWORD is not set.")
    _prepare_client._client.login(*login_info)
    logger.info("logged in")
    return _prepare_client._client


def _prepare_blob_ref(thumb_image_path: Path):
    with open(thumb_image_path, 'rb') as f:
        _upload = client.com.atproto.repo.upload_blob(f)
    return _upload.blob


def update_live_status(
        thumb_image_path: Path,
        twitch_user_name: str,
        title: str,
        description: str,
        duration_minutes: int
):
    if not _is_valid_username(twitch_user_name):
        logger.error("username is not valid")
        raise ValueError("The username does not meet the constraints.")
    # login情報がなければステータス更新せずスキップ
    if ~all([os.getenv('BSKY_USER_NAME'), os.getenv('BSKY_PASSWORD')]):
        logger.warning("Bsky username and password were not set. Continue without updating bsky status.")
        return None
    bsky_client = _prepare_client()
    _embed = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(
            uri=f"https://www.twitch.tv/{twitch_user_name}",
            title=title,
            description=description,
            thumb=_prepare_blob_ref(thumb_image_path)
        )
    )
    logger.debug(_embed)
    _status_record = models.AppBskyActorStatus.Record(
        status="app.bsky.actor.status#live",
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        duration_minutes=duration_minutes,
        embed=_embed,
    )

    _data = models.ComAtprotoRepoPutRecord.Data(
        repo=bsky_client.me.did,
        collection="app.bsky.actor.status",
        rkey="self",
        record=_status_record,
    )
    response = bsky_client.com.atproto.repo.put_record(_data)
    return response
