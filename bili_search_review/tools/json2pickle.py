import sys
import json
import pickle


def main():
    if len(sys.argv) < 2 or not sys.argv[1].endswith(".json"):
        print("Please specify a JSON file!")
        exit(1)
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    pickle_file = json_file.replace(".json", ".pickle")
    with open(pickle_file, "wb") as f:
        pickle.dump(data, f, protocol=5)


if __name__ == "__main__":
    main()
