import os
import sys
import json
import pickle

# 是否跳过未知地区
SKIP_UNKNOWN_LOC = True


def load_reviews(filename: str):
    if filename.endswith(".json"):
        with open(filename, mode="r", encoding="utf-8") as f:
            data = json.load(f)
    if filename.endswith(".pickle"):
        with open(filename, mode="rb") as f:
            data = pickle.load(f)

    reviews = []
    for video in data:
        comments = video["comments"]
        if comments is None:
            continue
        reviews.extend(comments)

    sub_reviews = []
    for review in reviews:
        comments = review.get("sub_replies", None)
        if comments is None:
            continue
        del review["sub_replies"]
        sub_reviews.extend(comments)

    reviews += sub_reviews
    return reviews


def dedup_reviews(reviews: list[dict]):
    dedup_review_set = set()
    dedup_reviews = []
    for review in reviews:
        if SKIP_UNKNOWN_LOC and review["location"] == "未知":
            continue

        key = str(sorted(review.items(), key=lambda p: p[0]))
        if key in dedup_review_set:
            continue

        dedup_review_set.add(key)
        dedup_reviews.append(review)
    return dedup_reviews


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
            # 发送者ID
            "member_id": review["mid"],
            # 发送者性别
            "member_sex": review["member"]["sex"],
            # 发送者昵称
            "member_nickname": review["member"]["uname"],
            # 评论内容
            "text": review["content"]["message"],
            # IP属地
            "location": review["reply_control"]
            .get("location", "IP属地：未知")
            .split("：")[1],
            # 点赞数量
            "like": review["like"],
            # 评论ID
            "rpid": review["rpid"],
            # 根评论ID
            "root_rpid": review["root"],
            # 父评论ID
            "parent_rpid": review["parent"],
            # Up主点赞
            "up_like": review["up_action"]["like"],
            # Up主回复
            "up_reply": review["up_action"]["reply"],
            # 发布时间
            "publish_time": review["ctime"],
            # 隐藏评论
            "invisible": review["invisible"],
        }
        for review in reviews
    ]

    reviews = dedup_reviews(reviews)

    result_path, _ = os.path.splitext(data_file)
    result_path += "_dedup.json"
    with open(
        result_path,
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(reviews, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
