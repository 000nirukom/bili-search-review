import asyncio
import json
import os

from bilibili_api import ResponseCodeException, search
from bilibili_api import login, user

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


async def main() -> None:
    print("请登录：")
    credential = login.login_with_qrcode()  # 二维码登陆
    try:
        credential.raise_for_no_bili_jct()  # 判断是否成功
        credential.raise_for_no_sessdata()  # 判断是否成功
    except Exception:
        print("登陆失败。")
        raise
    self_info = await user.get_self_info(credential)
    print("欢迎，", self_info["name"], "!")

    keyword = input("请输入关键词：").strip()
    if not keyword:
        print("请勿输入空关键词！")
        return
    max_page = int(input("请输入搜索最大页数 (最高50): "))
    assert max_page <= 50, "页数超出最大限制！"
    if os.name == "nt":
        os.system(f"title {keyword}")
    else:
        pass
    videos = await scrap(
        keyword=keyword,
        max_page=max_page,
        # 凭证
        credential=credential,
    )
    with open(f"videos_{keyword}.json", "w+", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False)


def _main():
    asyncio.run(main())


if __name__ == "__main__":
    _main()
