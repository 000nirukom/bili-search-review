import os
import json
import asyncio
import logging

from tqdm import tqdm
from bilibili_api import comment
from bilibili_api.comment import OrderType
from bilibili_api.exceptions.ResponseCodeException import ResponseCodeException

from bili_search_review.interval import (
    INTERVAL_PER_ROOT_REPLY,
    INTERVAL_PER_ROOT_REPLY_PAGE,
)
from bili_search_review.interval import INTERVAL_PER_SUB_REPLY_PAGE

logger = logging.getLogger(__name__)


async def fetch_comments(reply, credential=None):
    """
    This will return list of original reply and sub-replies
    """
    oid = reply["oid"]
    rpid = reply["rpid"]

    cache_dir = f"cache_v2/review/{oid}/"
    os.makedirs(cache_dir, exist_ok=True)

    cache_file_path = os.path.join(cache_dir, f"{rpid}.json")
    if os.path.exists(cache_file_path):
        logger.info(f"skipping rp{rpid}: cache existing")
        with open(cache_file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    logger.info(f"start: av{oid} - rp{rpid}")

    skip_cache = False
    try:
        # may fetch partial sub comments here: exception case
        sub_replies = await fetch_sub_comments(oid, rpid, credential)
    except ResponseCodeException:
        sub_replies = []
        skip_cache = True

    result = [reply] + sub_replies

    if not skip_cache:
        with open(cache_file_path, "w+", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)

    # We don't sleep if we skipped
    await asyncio.sleep(INTERVAL_PER_ROOT_REPLY)
    return result


async def fetch_sub_comments(oid: int, rpid: int, credential=None):
    """
    Fetch sub-reviews from specified review

    :return: sub-reviews as an array
    """
    page_size = 20
    cur_comment = comment.Comment(
        oid=oid,
        rpid=rpid,
        type_=comment.CommentResourceType.VIDEO,
        credential=credential,
    )

    first_sub = await cur_comment.get_sub_comments(page_size=page_size)

    sub_count = first_sub["page"]["count"]
    logger.info(f"rp{rpid}: {sub_count} sub-reviews")

    sub_comments = []
    sub_comments.extend(first_sub["replies"])

    def round(count: int):
        return (count + page_size - 1) // page_size

    end = round(sub_count) + 1
    if end <= 2:
        return sub_comments

    for page_index in tqdm(range(2, end), desc="Sub-Replies"):
        logger.info(f"rp{rpid}: fetching page {page_index}")
        try:
            sub = await cur_comment.get_sub_comments(
                # 页码
                page_index=page_index,
                # 页大小
                page_size=page_size,
            )
        except ResponseCodeException:
            return sub_comments

        sub_comments.extend(sub["replies"])
        await asyncio.sleep(INTERVAL_PER_SUB_REPLY_PAGE)
    return sub_comments


async def get_all_comments(v_aid: int, credential=None):
    comments = []
    page = 1
    count = 0

    while True:
        logger.info(f"fetching page {page} for video av{v_aid}...")
        c = await comment.get_comments(
            v_aid, comment.CommentResourceType.VIDEO, page, credential=credential
        )

        replies = c["replies"]
        if replies is None:
            break

        comments.extend(replies)
        count += c["page"]["size"]
        page += 1

        if count >= c["page"]["count"]:
            break

        await asyncio.sleep(INTERVAL_PER_ROOT_REPLY_PAGE)

    total_list = []
    for reply in tqdm(comments, desc="Replies"):
        cur_replies = await fetch_comments(reply, credential)
        total_list.extend(cur_replies)

    return total_list


async def get_hot_comments(v_aid: int, credential=None):
    # 最热评论
    hot_comments = await comment.get_comments(
        v_aid,
        type_=comment.CommentResourceType.VIDEO,
        order=OrderType.LIKE,
        credential=credential,
    )
    hot_replies = hot_comments["replies"]

    if hot_replies is None:
        return []

    total_list = []
    for reply in tqdm(hot_replies, desc="Replies"):
        cur_replies = await fetch_comments(reply, credential)
        total_list.extend(cur_replies)

    return total_list
