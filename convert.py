import csv
import json
import os

def generate_json(base_dir):
    cricket_data = {
        "test": {"batting": {}, "bowling": {}},
        "odi": {"batting": {}, "bowling": {}},
        "t20": {"batting": {}, "bowling": {}}
    }

    formats = ["test", "odi", "t20"]
    types = ["batting", "bowling"]
    years = range(2011, 2026)

    for fmt in formats:
        for typ in types:
            for year in years:
                file_name = f"{fmt}_{typ}_{year}.csv"
                file_path = os.path.join(base_dir, file_name)

                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as csv_file:
                        reader = csv.DictReader(csv_file)
                        data = list(reader)

                    cricket_data[fmt][typ][str(year)] = data

    return cricket_data


def save_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)


def main():
    base_dir = "./cricket_stats"
    output_file = "cricket_data.json"

    cricket_data = generate_json(base_dir)
    save_json(cricket_data, output_file)

    print(f"JSON file saved to {output_file}")


if __name__ == "__main__":
    main()
