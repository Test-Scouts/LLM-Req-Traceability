"""
Evaluates the performance of different runs by checking the out/
folder.

Uses the format `out/{model}/{date}/{time}/res.json`, which
is the outut from `send_data.py` and `send_data_gpt.py`.
"""

import csv
import json
import os
import sys

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    # Load the set of tests
    tests: set[str]
    with open(os.getenv("TEST_PATH"), "r") as f:
        reader: csv.DictReader = csv.DictReader(f)
        tests = {row["ID"] for row in reader}
    
    # Maps Req ID -> Test IDs
    map_: dict[str, set[str]]
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

        map_ = map_ = {
            e["Req ID"]: (set(e["Test IDs"]) if e["Test IDs"] else set())
            for e in tmp
        }

    print("Info - REST Mapping:\nInfo - {}".format(json.dumps({k: tuple(map_[k]) for k in map_}, indent=2).replace("\n", "\nInfo - ")))

    # Evaluate results of every output
    for model in os.listdir(f"./out"):
        for day in os.listdir(f"./out/{model}"):
            for time in os.listdir(f"./out/{model}/{day}"):
                # Skip outputs that already have been evaluated to save time and compute
                # Also skip folders with no res.json
                dir_: list[str] = os.listdir(f"./out/{model}/{day}/{time}")
                if "eval.log" in dir_ \
                    or "res.json" not in dir_:
                    print(f"Info - Skipping ./out/{model}/{day}/{time}")
                    continue

                out_path: str = f"./out/{model}/{day}/{time}/res.json"
                print(f"Info - Evaluating {out_path}")

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

                    if not req_id:
                        sys.stderr.write(f"Error - ./out/{model}/{day}/{time}: Faulty requirement ID\n")
                        continue

                    actual_tests: set[str] = set(req["tests"].replace(" ", "").split(",")) if req["tests"] else set()

                    expected_tests: set[str] = map_.get(req_id, None)
                    # Skip if req ID returned None
                    if expected_tests is None:
                        sys.stderr.write(f"Error - ./out/{model}/{day}/{time}: Faulty requirement ID ({req_id})\n")
                        continue

                    outliers: set[str] = actual_tests - tests

                    if outliers:
                        sys.stderr.write(f"Error - ./out/{model}/{day}/{time}: Faulty test IDs for {req_id}:\n")
                        for o in outliers:
                            sys.stderr.write(f"Error - \t\t{o}\n")

                        # Remove outliers
                        actual_tests -= outliers

                    print(f"Info - ./out/{model}/{day}/{time}: {req_id}:")
                    # for t in actual_tests:
                        # print(f"Info - ./out/{model}/{day}/{time}: Test ID {t} for requirement {req_id}")
                    print(f"Info - \t\t{expected_tests = }")
                    print(f"Info - \t\t{actual_tests   = }")
                    # Positives
                    tps: set[str] = actual_tests & expected_tests
                    tpsn: int = len(tps)
                    print(f"Info - \t\t({tpsn}) {tps = }")
                    fps: set[str] = actual_tests - expected_tests
                    fpsn: int = len(fps)
                    print(f"Info - \t\t({fpsn}) {fps = }")

                    # Negatives
                    expected_ns: set[str] = tests - expected_tests
                    actual_ns: set[str] = tests - actual_tests

                    tns: set[str] = actual_ns & expected_ns
                    tnsn: int = len(tns)
                    print(f"Info - \t\t({tnsn}) {tns = }")
                    fns: set[str] = actual_ns - expected_ns
                    fnsn: int = len(fns)
                    print(f"Info - \t\t({fnsn}) {fns = }")

                    curr_n: int = tpsn + fpsn + tnsn + fnsn
                    
                    expected_curr_n: int = len(tests)
                    if curr_n != expected_curr_n:
                        sys.stderr.write(f"Error - \t\tExpected curr_n = {expected_curr_n}, got {curr_n = }\n")
                    else:
                        print(f"Info - \t\t{curr_n = }")

                    n += curr_n
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
