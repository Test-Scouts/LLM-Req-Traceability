"""
Evaluates the performance of different runs by checking the out/
folder.

Uses the format `out/{model}/{date}/{time}/res.json`, which
is the outut from `send_data.py` and `send_data_gpt.py`.
"""

import csv
import datetime
from functools import reduce
import json
import os
from contextlib import redirect_stdout
import argparse

from dotenv import load_dotenv

from .core.rest import RESTSpecification
from .core.stats import Stats


now: datetime.datetime = datetime.datetime.now()

date: str = str(now.date())
time: str = str(now.time())

res_dir: str = f"./res/{date}/{time}"
log_path: str = f"{res_dir}/eval.log"


def main() -> None:
    parser = argparse.ArgumentParser(description="Process file information.")
    parser.add_argument("--data", "-d", dest="data", type=str, default= "GBG", help="Customize the dataset, not case sensitive. Use MIX for the mix dataset, Mix-small for mix-small-dataset, BTHS for the BTHS dataset, and GBG for the GBG dataset. Default is GBG.")

    args = parser.parse_args()
    data: str = args.data.lower()

    load_dotenv()

    if data == "mix":
        print("Info - Using MIX data")
        req_path = os.getenv("MIX_REQ_PATH")
        test_path = os.getenv("MIX_TEST_PATH")
        mapping_path = os.getenv("MIX_MAP_PATH")
    elif args.data.lower() == "mix-small":
        print("Using MIX-small data")
        req_path = os.getenv("S_MIX_REQ_PATH")
        test_path = os.getenv("S_MIX_TEST_PATH")
        mapping_path = os.getenv("S_MIX_MAP_PATH")
    elif args.data.lower() == "bths":
        print("Using BTHS data")
        req_path = os.getenv("BTHS_REQ_PATH")
        test_path = os.getenv("BTHS_TEST_PATH")
        mapping_path = os.getenv("BTHS_MAP_PATH")
    else:
        print("Info - Using GBG data")
        req_path = os.getenv("GBG_REQ_PATH")
        test_path = os.getenv("GBG_TEST_PATH")
        mapping_path = os.getenv("GBG_MAP_PATH")

    print(f"Info - Requirements path: {req_path}")
    print(f"Info - Tests path: {test_path}")
    print(f"Info - Mapping path: {mapping_path}")
    
    # Load the set of tests
    tests: set[str]
    with open(test_path, "r") as f:
        reader: csv.DictReader = csv.DictReader(f)
        tests = {row["ID"] for row in reader}

    specs: RESTSpecification = RESTSpecification.load_specs(
        req_path, test_path
    )
    
    # Maps Req ID -> Test IDs
    map_: dict[str, set[str]]
    # Load the mappings
    with open(mapping_path, "r") as f:
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

    prevalence: float = reduce(lambda acc, key: acc + len(map_[key]), map_, 0) / specs.n

    res_path: str = f"{res_dir}/res.log"

    print("Info - REST Mapping:\nInfo - {}".format(json.dumps({k: tuple(map_[k]) for k in map_}, indent=2).replace("\n", "\nInfo - ")))

    # Evaluate results of every output
    for m in os.listdir(f"./out"):
        # Model stats
        all_n: list[int] = []
        all_tp: list[int] = []
        all_tn: list[int] = []
        all_fp: list[int] = []
        all_fn: list[int] = []

        all_accuracy: list[float] = []
        all_recall: list[float] = []
        all_precision: list[float] = []
        all_specificity: list[float] = []
        all_balanced_accuracy: list[float] = []
        all_f1: list[float] = []

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

                    print(f"Info - ./out/{m}/{d}/{t}: {req}:")

                    # Positives
                    curr_tp_set: set[str] = actual_tests & expected_tests
                    curr_tp_count: int = len(curr_tp_set)
                    print(f"Info - \t\t({curr_tp_count}) {curr_tp_set = }")

                    curr_fp_set: set[str] = actual_tests - expected_tests
                    curr_fp_count: int = len(curr_fp_set)
                    print(f"Info - \t\t({curr_fp_count}) {curr_fp_set = }")

                    # Negatives
                    expected_ns: set[str] = tests - expected_tests
                    actual_ns: set[str] = tests - actual_tests

                    curr_tn_set: set[str] = actual_ns & expected_ns
                    curr_tn_count: int = len(curr_tn_set)
                    print(f"Info - \t\t({curr_tn_count}) {curr_tn_set = }")

                    curr_fn_set: set[str] = actual_ns - expected_ns
                    curr_fn_count: int = len(curr_fn_set)
                    print(f"Info - \t\t({curr_fn_count}) {curr_fn_set = }")

                    curr_n: int = curr_tp_count + curr_fp_count + curr_tn_count + curr_fn_count
                    
                    expected_curr_n: int = len(tests)
                    if curr_n != expected_curr_n:
                        print(f"Error - \t\tExpected curr_n = {expected_curr_n}, got {curr_n = }")
                    else:
                        print(f"Info - \t\t{curr_n = }")

                    n += curr_n
                    tp += curr_tp_count
                    tn += curr_tn_count
                    fp += curr_fp_count
                    fn += curr_fn_count

                all_n.append(n)
                all_tp.append(tp)
                all_tn.append(tn)
                all_fp.append(fp)
                all_fn.append(fn)
                
                accuracy: float = (tp + tn) / n if n != 0 else 0.0
                recall: float = tp / (tp + fn) if tp + fn != 0 else 0.0
                precision: float = tp / (tp + fp) if tp + fp != 0 else 0.0
                specificity: float = tn / (tn + fn) if tn + fn != 0 else 0.0
                balanced_accuracy: float = (precision + specificity) / 2
                f1: float = 2 * (recall * precision) / (recall + precision) if recall + precision != 0 else 0.0

                all_accuracy.append(accuracy)
                all_recall.append(recall)
                all_precision.append(precision)
                all_specificity.append(specificity)
                all_balanced_accuracy.append(balanced_accuracy)
                all_f1.append(f1)

                eval_path = f"{os.path.dirname(out_path)}/eval.json"
                data: dict = {
                    "prevalence": prevalence,
                    "n": n,
                    "tp": tp,
                    "tn": tn,
                    "fp": fp,
                    "fn": fn,
                    "accuracy": accuracy,
                    "balanced_accuracy": balanced_accuracy,
                    "f1": f1,
                    "recall": recall,
                    "precision": precision,
                    "specificity": specificity
                }

                with open(eval_path, "w+") as f:
                    json.dump(data, f, indent=2)

                with open(res_path, "a+") as f:
                    f.write(f"./out/{m}/{d}/{t}\n")
                    json.dump(data, f, indent=2)
                    f.write("\n")

        data: dict = {
            "prevalence": prevalence,
            "all_n": Stats("all_n", all_n).as_dict,
            "all_tp": Stats("all_tp", all_tp).as_dict,
            "all_tn": Stats("all_tn", all_tn).as_dict,
            "all_fp": Stats("all_fp", all_fp).as_dict,
            "all_fn": Stats("all_fn", all_fn).as_dict,
            "all_accuracy": Stats("all_accuracy", all_accuracy).as_dict,
            "all_balanced_accuracy": Stats("all_balanced_accuracy", all_balanced_accuracy).as_dict,
            "all_f1": Stats("all_f1", all_f1).as_dict,
            "all_recall": Stats("all_recall", all_recall).as_dict,
            "all_precision": Stats("all_precision", all_precision).as_dict,
            "all_specificity": Stats("all_specificity", all_specificity).as_dict,
        }

        print(f"Info - Logging total and avarage metrics for {m}")
        with open(f"{res_dir}/{m}.json", "w") as f:
            f.write(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    os.makedirs(res_dir, exist_ok=True)

    # Redirect stdout to a log file
    with open(log_path, "a+") as out:
        with redirect_stdout(out):
            main()
