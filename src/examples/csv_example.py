import csv


def main() -> None:
    # Open requirements file
    with open("./example_data/Snake_Game_Requirements.csv", "r", newline="") as f:
        # Sniff the dialect
        dialect: csv.Dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)

        # Parse the csv to a dict
        reader: csv.DictReader = csv.DictReader(f, dialect=dialect)
        for r in reader:
            print(r)


if __name__ == "__main__":
    main()
