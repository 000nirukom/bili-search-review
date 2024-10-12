import os
import json
import asyncio
import logging


from bilibili_api import user

from bili_search_review.scrap import scrap
from bili_search_review.utils import login_with_qr, login_with_qr_term

logger = logging.getLogger(__name__)


async def main() -> None:
    try:
        credential = login_with_qr()
    except ImportError:
        credential = login_with_qr_term()
    self_info = await user.get_self_info(credential)
    logger.info(f"Logged as {self_info["name"]}, mid: {self_info["mid"]}")

    keyword = input("请输入关键词：").strip()
    if not keyword:
        print("请勿输入空关键词！")
        return
    max_page = int(input("请输入搜索最大页数 (最高50): "))
    assert max_page <= 50, "页数超出最大限制！"

    if os.name == "nt":
        os.system(f"title {keyword}")

    videos = await scrap(
        keyword=keyword,
        max_page=max_page,
        credential=credential,
    )
    with open(f"videos_{keyword}.json", "w+", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False)


def _main():
    asyncio.run(main())


if __name__ == "__main__":
    _main()
