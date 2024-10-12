import os
import json
import asyncio

from bilibili_api import comment
from bilibili_api.comment import OrderType

from bili_search_review.interval import SUB_REPLY_INTERVAL
from bili_search_review.interval import SUB_REPLY_PAGE_INTERVAL


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
        print(f"skipping fetch sub-reviews from {rpid} due to cache")
        with open(cache_file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"fetching sub-reviews for reply {rpid} from av{oid}")
    sub_replies = await fetch_sub_comments(oid, rpid, credential)

    result = [reply] + sub_replies
    with open(cache_file_path, "w+", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    # We don't sleep if we skipped
    await asyncio.sleep(SUB_REPLY_INTERVAL)
    return result


async def fetch_sub_comments(oid: int, rpid: int, credential=None):
    """
    Fetch sub-reviews from specified review

    :return: sub-reviews as an array
    """
    c = comment.Comment(
        oid=oid,
        rpid=rpid,
        type_=comment.CommentResourceType.VIDEO,
        credential=credential,
    )
    page_size = 20
    print("fetching first page...")
    first_sub = await c.get_sub_comments(page_size=page_size)
    sub_count = first_sub["page"]["count"]
    print(f"found {sub_count} sub-reviews")

    sub_comments = []
    sub_comments.extend(first_sub["replies"])

    for page_index in range(2, (sub_count + page_size - 1) // page_size + 1):
        c = comment.Comment(
            oid=oid,
            rpid=rpid,
            type_=comment.CommentResourceType.VIDEO,
            credential=credential,
        )
        print(f"fetching page {page_index}...")
        sub = await c.get_sub_comments(
            # 页码
            page_index=page_index,
            # 页大小
            page_size=page_size,
        )
        sub_comments.extend(sub["replies"])
        await asyncio.sleep(SUB_REPLY_PAGE_INTERVAL)
    return sub_comments


async def get_hot_comments(v_aid: int, credential=None):
    # 最热评论
    hot_comments = await comment.get_comments(
        v_aid,
        type_=comment.CommentResourceType.VIDEO,
        order=OrderType.LIKE,
        credential=credential,
    )
    replies = hot_comments["replies"]

    total_list = []
    for reply in replies:
        cur_replies = await fetch_comments(reply, credential)
        total_list.extend(cur_replies)

    return total_list
