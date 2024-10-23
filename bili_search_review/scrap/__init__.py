import asyncio
import logging

from tqdm import tqdm
from bilibili_api import search

from bili_search_review.hot import get_hot_comments
from bili_search_review.interval import INTERVAL_PER_VIDEO_PAGE
from bili_search_review.interval import INTERVAL_PER_VIDEO

logger = logging.getLogger(__name__)


async def scrap(keyword: str, max_page: int = 50, credential=None):
    videos = []
    try:
        for page in tqdm(range(1, max_page + 1), desc="Pages"):
            await asyncio.sleep(INTERVAL_PER_VIDEO_PAGE)

            try:
                result = await search.search(keyword, page=page)
            except Exception as e:
                logger.error(f"Search failed: {e.__class__.__name__}: {e.__cause__}")
                continue

            logger.info(f"keyword {keyword}, page {page}")
            r = [r for r in result["result"] if r["result_type"] == "video"][0]
            r = r["data"]
            for d in tqdm(r, desc="Videos"):
                aid = d["aid"]
                title: str = d["title"]
                # process HTML tag in raw content
                title = title.replace('<em class="keyword">', "")
                title = title.replace("</em>", "")
                if aid == 0:
                    logger.warning(f"Skipping invalid item {title}")
                    continue
                author = d["author"]
                author_mid = d["mid"]
                logger.info(f"start: av{aid} - {title}")
                await asyncio.sleep(INTERVAL_PER_VIDEO)
                try:
                    comments = await get_hot_comments(aid, credential)
                except Exception as e:
                    logger.error(
                        f"Hot comment failed: {e.__class__.__name__}: {e.__cause__}"
                    )
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
    except KeyboardInterrupt:
        # early exit on Ctrl-C emit
        pass

    return videos
