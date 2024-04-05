import csv
import json
import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    # Load the set of tests
    tests: set[str]
    with open(os.getenv("TEST_PATH"), "r") as f:
        reader: csv.DictReader = csv.DictReader(f)
        tests = {row["ID"] for row in reader}
    
    # Maps Req ID -> Test IDs
    map_: dict[str, list[str]]
    # Load the mappings
    with open(os.getenv("MAP_PATH"), "r") as f:
        fields: list[str] = [
            "Req ID",
            "Test IDs"
        ]
        reader: csv.DictReader = csv.DictReader(f)

        # {"Req ID": <Req ID>, "Test IDs": <Test IDs>} for each row
        tmp: list[dict[str, str | list[str]]] = [
            {k: row[k] for k in row.keys() if k in fields}
            for row in reader
        ]

        for e in tmp:
            e["Test IDs"] = e["Test IDs"].replace(" ", "").split(",") if e["Test IDs"] else []

        map_ = {e["Req ID"]: e["Test IDs"] for e in tmp}

    # Evaluate results of every output
    for model in os.listdir(f"./out"):
        for day in os.listdir(f"./out/{model}"):
            for time in os.listdir(f"./out/{model}/{day}"):
                # Skip outputs that already have been evaluated to save time and compute
                if "eval.log" in os.listdir(f"./out/{model}/{day}/{time}"):
                    continue

                out_path: str = f"./out/{model}/{day}/{time}/res.json"

                # Load the tool output
                res: list[dict[str, str]]
                with open(out_path, "r") as f:
                    res = json.load(f)

                # Values for confusion matrix
                n: int = 0
                tp: int = 0
                tn: int = 0
                fp: int = 0
                fn: int = 0

                for req in res:
                    req_id: str = req["requirementID"]
                    actual_tests: set[str] = set(req["tests"].replace(" ", "").split(","))

                    expected_tests: set[str] = set(map_.get(req_id, []))

                    tps: set[str] = actual_tests & expected_tests
                    tpsn: int = len(tps)
                    fps: set[str] = actual_tests - expected_tests
                    fpsn: int = len(fps)

                    # Negatives
                    expected_ns: set[str] = tests - expected_tests
                    actual_ns: set[str] = tests - actual_tests

                    tns: set[str] = actual_ns & expected_ns
                    tnsn: int = len(tns)
                    fns: set[str] = actual_ns - expected_ns
                    fnsn: int = len(fns)

                    n += tpsn + fpsn + tnsn + fnsn
                    tp += tpsn
                    tn += tnsn
                    fp += fpsn
                    fn += fnsn
                
                accuracy: float = 100 * (tp + tn) / n if n != 0 else 0
                recall: float = 100 * tp / (tp + fn) if tp + fn != 0 else 0
                precision: float = 100 * tp / (tp + fp) if tp + fp != 0 else 0

                eval_path = f"{os.path.dirname(out_path)}/eval.log"
                lines: list[str] = [
                    f"{n=}",
                    f"{tp=}",
                    f"{tn=}",
                    f"{fp=}",
                    f"{fn=}",
                    f"{accuracy=}%",
                    f"{recall=}%",
                    f"{precision=}%"
                ]
                with open(eval_path, "w+") as f:
                    f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()