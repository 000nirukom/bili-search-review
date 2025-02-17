import os
import sys
import json

import polars as pl

SKIP_UNKNOWN_LOC = os.environ.get("SKIP_UNKNOWN_LOC", False)


def load_reviews(filename: str):
    if filename.endswith(".json"):
        with open(filename, mode="r", encoding="utf-8") as f:
            data = json.load(f)

    reviews = []
    for video in data:
        comments = video["comments"]
        if comments is None:
            continue

        for comment in comments:
            video: dict
            comment["_video_title"] = video["title"]
            comment["_author"] = video.get("author")
            comment["_author_mid"] = video.get("author_mid")

        reviews.extend(comments)

    return reviews


def dedup_reviews(reviews: list[dict]):
    dedup_review_set = set()
    dedup_reviews_ = []
    for review in reviews:
        if SKIP_UNKNOWN_LOC and review["location"] == "未知":
            continue

        key = str(sorted(review.items(), key=lambda p: p[0]))
        if key in dedup_review_set:
            continue

        dedup_review_set.add(key)
        dedup_reviews_.append(review)
    return dedup_reviews_


def main():
    if len(sys.argv) < 2:
        print("Please specify a JSON/Pickle file!")
        exit(1)
    data_file = sys.argv[1]
    if not data_file.endswith(".json") and not data_file.endswith(".pickle"):
        print("Only JSON/Pickle files are supported!")
        exit(1)
    if not os.path.isfile(data_file):
        print("Input path must be a file!")
        exit(1)
    reviews = load_reviews(data_file)
    reviews = [
        {
            # 评论ID
            "rpid": review["rpid"],
            # 根评论ID
            "root_rpid": review["root"],
            # 父评论ID
            "parent_rpid": review["parent"],
            # 评论内容
            "text": review["content"]["message"],
            # 视频 AVID
            "video_aid": review["oid"],
            # 视频标题
            "video_title": review["_video_title"],
            # 视频作者昵称
            "author_name": review["_author"],
            # 视频作者ID
            "author_mid": review["_author_mid"],
            # 发送者昵称
            "publisher_name": review["member"]["uname"],
            # 发送者ID
            "publisher_mid": review["mid"],
            # 发送者性别
            "publisher_sex": review["member"]["sex"],
            # 发送者用户等级
            "publisher_level": review["member"]["level_info"]["current_level"],
            # 发送者硬核会员
            "publisher_senior": review["member"]["senior"].get("status", 0) == 2,
            # 发送者大会员 0: 非大会员, 1: 月费大会员, 2: 年费大会员
            "publisher_vip_type": review["member"]["vip"]["vipType"],
            # IP属地
            "publisher_location": review["reply_control"]
            .get("location", "IP属地：未知")
            .split("：")[1],
            # 点赞数量
            "like": review["like"],
            # Up主点赞
            "up_like": review["up_action"]["like"],
            # Up主回复
            "up_reply": review["up_action"]["reply"],
            # 隐藏评论
            "invisible": review["invisible"],
            # 发布时间
            "publish_time": review["ctime"],
        }
        for review in reviews
    ]

    reviews = dedup_reviews(reviews)

    result_path, _ = os.path.splitext(data_file)

    result_json_path = f"{result_path}_dedup.json"
    result_xlsx_path = f"{result_path}_dedup.xlsx"

    with open(
        result_json_path,
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(reviews, f, ensure_ascii=False)

    types = {
        "rpid": str,
        "root_rpid": str,
        "parent_rpid": str,
        "text": str,
        "video_aid": str,
        "video_title": str,
        "author_name": str,
        "author_mid": str,
        "publisher_name": str,
        "publisher_mid": str,
        "publisher_sex": str,
        "publisher_level": int,
        "publisher_senior": bool,
        "publisher_vip_type": int,
        "publisher_location": str,
        "like": int,
        "up_like": bool,
        "up_reply": bool,
        "invisible": bool,
        # unix timestamp
        "publish_time": int,
    }
    df = pl.DataFrame(reviews, schema=types)
    # 发布时间设置为 UTC+8 时间
    df = df.with_columns(
        pl.from_epoch(
            pl.col("publish_time"),
            time_unit="s",
        )
        .dt.replace_time_zone("UTC")
        .dt.convert_time_zone("Asia/Shanghai")
        .dt.replace_time_zone(None),
    )
    df.write_excel(
        result_xlsx_path,
        include_header=True,
    )


if __name__ == "__main__":
    main()
