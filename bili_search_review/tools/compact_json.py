import sys
import json


def main():
    if len(sys.argv) < 2 or not sys.argv[1].endswith(".json"):
        print("Please specify a JSON file!")
        exit(1)
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(json_file, "w+", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
