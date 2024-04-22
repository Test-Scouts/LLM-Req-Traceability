"""
Evaluates the performance of different runs by checking the out/
folder.

Uses the format `out/{model}/{date}/{time}/res.json`, which
is the outut from `send_data.py` and `send_data_gpt.py`.
"""

import csv
import datetime
import json
import os
from contextlib import redirect_stdout

from dotenv import load_dotenv


now: datetime.datetime = datetime.datetime.now()

date: str = str(now.date())
time: str = str(now.time())

res_dir: str = f"./res/{date}/{time}-label"
log_path: str = f"{res_dir}/eval.log"


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

    res_path: str = f"{res_dir}/res.log"

    print("Info - REST Mapping:\nInfo - {}".format(json.dumps({k: tuple(map_[k]) for k in map_}, indent=2).replace("\n", "\nInfo - ")))

    # Evaluate results of every output
    for m in os.listdir(f"./out"):
        # Model stats
        total_n: int = 0
        total_tp: int = 0
        total_tn: int = 0
        total_fp: int = 0
        total_fn: int = 0

        for d in os.listdir(f"./out/{m}"):
            for t in os.listdir(f"./out/{m}/{d}"):
                out_path: str = f"./out/{m}/{d}/{t}/res.json"
                print(f"Info - Evaluating {out_path}")

                # Load the tool output
                res: dict[str, list[str]]
                with open(out_path, "r") as f:
                    res = json.load(f)

                # Values for confusion matrix
                n: int = 0
                tp: int = 0
                tn: int = 0
                fp: int = 0
                fn: int = 0

                for req in res:
                    actual_tests: set[str] = set(res[req])

                    expected_tests: set[str] = map_.get(req, None)
                    # Skip if req ID returned None
                    if expected_tests is None:
                        print(f"Error - ./out/{m}/{d}/{t}: Faulty requirement ID ({req})")
                        continue

                    outliers: set[str] = actual_tests - tests

                    if outliers:
                        print(f"Error - ./out/{m}/{d}/{t}: Faulty test IDs for {req}:")
                        for o in outliers:
                            print(f"Error - \t\t{o}")

                        # Remove outliers
                        actual_tests -= outliers

                    print(f"Info - ./out/{m}/{d}/{t}: {req}:")

                    is_positive: bool = bool(expected_tests)
                    is_labelled_positive: bool = bool(actual_tests)

                    n += 1
                    tp += is_positive and is_labelled_positive
                    tn += not is_positive and not is_labelled_positive
                    fp += not is_positive and is_labelled_positive
                    fn += is_positive and not is_labelled_positive
                
                accuracy: float = 100 * (tp + tn) / n if n != 0 else 0.0
                recall: float = 100 * tp / (tp + fn) if tp + fn != 0 else 0.0
                precision: float = 100 * tp / (tp + fp) if tp + fp != 0 else 0.0

                eval_path = f"{os.path.dirname(out_path)}/label-eval.log"
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
                res_str: str = "\n".join(lines) + "\n"

                with open(eval_path, "w+") as f:
                    f.write(res_str)

                with open(res_path, "a+") as f:
                    f.write(f"./out/{m}/{d}/{t}\n{res_str}\n")

                total_n += n
                total_tp += tp
                total_tn += tn
                total_fp += fp
                total_fn += fn

        avg_accuracy: float = 100 * (total_tp + total_tn) / total_n if total_n != 0 else 0.0
        avg_recall: float = 100 * total_tp / (total_tp + total_fn) if total_tp + total_fn != 0 else 0.0
        avg_precision: float = 100 * total_tp / (total_tp + total_fp) if total_tp + total_fp != 0 else 0.0

        lines: list[str] = [
            f"{total_n=}",
            f"{total_tp=}",
            f"{total_tn=}",
            f"{total_fp=}",
            f"{total_fn=}",
            f"{avg_accuracy=}%",
            f"{avg_recall=}%",
            f"{avg_precision=}%"
        ]

        print(f"Info - Logging total and avarage metrics for {m}")
        with open(f"{res_dir}/{m}.log", "w") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(res_dir, exist_ok=True)

    # Redirect stdout to a log file
    with open(log_path, "a+") as out:
        with redirect_stdout(out):
            main()
