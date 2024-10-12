import asyncio

from bilibili_api import ResponseCodeException, search

from bili_search_review.hot import get_hot_comments
from bili_search_review.interval import PAGE_FETCH_INTERVAL
from bili_search_review.interval import REPLY_FETCH_INTERVAL


async def scrap(keyword: str, max_page: int = 50, credential=None):
    videos = []
    for page in range(1, max_page + 1):
        await asyncio.sleep(PAGE_FETCH_INTERVAL)
        try:
            result = await search.search(keyword, page=page)
        except ResponseCodeException as e:
            print(f"{e.__class__}: {e}")
            continue
        # pylint: disable=broad-except
        except Exception as e:
            print(f"搜索失败 {e.__class__}: {e}")
            continue
        print(f"fetching page {page} of keyword {keyword}")
        r = [r for r in result["result"] if r["result_type"] == "video"][0]
        r = r["data"]
        for d in r:
            aid = d["aid"]
            title: str = d["title"]
            title = title.replace('<em class="keyword">', "")
            title = title.replace("</em>", "")
            if aid == 0:
                print(f"Skipping invalid item {title}")
                continue
            author = d["author"]
            author_mid = d["mid"]
            print(f"fetching comments from av{aid} - {title}...")
            await asyncio.sleep(REPLY_FETCH_INTERVAL)
            try:
                comments = await get_hot_comments(aid, credential)
            except ResponseCodeException as e:
                print(f"{e.__class__}: {e}")
                continue
            # pylint: disable=broad-except
            except Exception as e:
                print(f"获取热评失败 {e.__class__}: {e}")
                continue
            videos.append(
                {
                    "aid": aid,
                    "title": title,
                    "author": author,
                    "author_mid": author_mid,
                    "comments": comments,
                }
            )

    return videos
