# Bili search review

Simple tool to fetch videos, get hot reviews (with sub reviews) of them.

NOTE: `EULA.md` must be accepted.

## Setup

```bash
python -m pip install -e .
# Optional dependencies for export-dedup
python -m pip install .[export]
```

## Run

```bash
python -m bili_search_review
```

## Structure

[`review`]: https://github.com/SocialSisterYi/bilibili-API-collect/blob/16d455ff098f46502eca2bafc7b96a2959a82f1b/docs/comment/readme.md#%E8%AF%84%E8%AE%BA%E6%9D%A1%E7%9B%AE%E5%AF%B9%E8%B1%A1

| Field      | Explanation | Type                 |
| ---------- | ----------- | -------------------- |
| aid        | AV Number   | `int`                |
| title      | Title       | `str`                |
| author     | Author      | `str`                |
| author_mid | Author mid  | `str`                |
| comments   | Reviews     | `list[`[`review`]`]` |

## Useful Commands

### Export reviews (with sub-reviews)

```bash
cat {JSON_FILE} | jq '.[].comments | select( . != null )' | jq -s
```

### Count all reviews

```bash
cat {JSON_FILE} | jq .[].comments.[].content.message | wc -l
```

### Count hot sub-reviews

```bash
cat {JSON_FILE} | jq .[].comments.[].replies.[].content.message | wc -l
```

