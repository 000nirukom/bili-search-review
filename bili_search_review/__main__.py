import json
import asyncio
import logging


import tqdm
import tqdm.contrib
import tqdm.contrib.logging
import tqdm.utils
from bilibili_api import user

from bili_search_review import VERSION
from bili_search_review.scrap import scrap
from bili_search_review.utils import login_checked

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("BSR %s" % VERSION)
    credential = login_checked()
    if credential is None:
        return

    self_info = await user.get_self_info(credential)
    logger.info("Logged as %s, mid: %d" % (self_info["name"], self_info["mid"]))

    keyword = input("Type keyword: ").strip()
    if not keyword:
        logger.error("Got empty keyword! exiting...")
        return
    max_page = int(input("Type max page number (<=50): "))
    assert max_page <= 50, "page number exceeds limits!"

    fetch_all = (
        input(
            "Would you like to fetch all comments, or just hot comments?\n(always with sub-comments; defaults to n) (Y/n):"
        )
        .lower()
        .strip()
        .startswith("y")
    )

    logger.info("Starting with keyword %s, max_page %d" % (keyword, max_page))
    with tqdm.contrib.logging.logging_redirect_tqdm():
        videos = await scrap(
            keyword=keyword,
            max_page=max_page,
            credential=credential,
            fetch_all=fetch_all,
        )
    with open(f"videos_{keyword}.json", "w+", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False)


def _main():
    asyncio.run(main())


if __name__ == "__main__":
    _main()
