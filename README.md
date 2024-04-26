# REST-at

Requirement Engineering and Software Testing Alignment Tool

This repository is dedicated for Bao's &amp; Nicole's thesis work.


## Running Scripts

Scripts nested in the `src/` should be run as modules to ensure that the relative imports work. E.g.:
```bash
$ python -m <path.to.module> # Omit the -.py file name extension
```

The scripts directly under `src/` can be run normally, E.g.:
```bash
$ python src/<script> # Include -.py file name extension here
```


## File Structure

The following file structures are **REQUIRED** for REST-at to work properly. All input files **MUST**
be in Comma Separated Value (`.csv`) format.

### Requirements Files

Requirements files must have the following rows (case sensitive) in whichever order:
- ID
- Feature
- Description

### Test Cases Files

Test cases files must have the following rows (case sensitive) in whichever order:
- ID
- Purpose
- Test steps

### Alignment Files

Only for development evaluations.
Alignment files must have the following rows (case sensitive) in whichever order:
- Req IDs
- Test ID
    - This column must consist of a list of Test IDs separated by commas


## Getting Started

### Prerequisites

- [Python 3.10](https://www.python.org/downloads/release/python-31014/) or later
- Hardware capable of running LLMs (large amounts of vRAM)
- A virtual Python environment (optional but recommended)

### Setting Up

Make sure that you're in the correct Python environment before you begin!

1. Clone this repository.
1. `cd` into the newly created directory.
1. Run `pip install -r requirements.txt`

### Running REST-at Scripts

Make sure that you're in the correct Python environment before you begin!

1. Create a `.env` file in the project root.
1. Add the following variables to the `.env` file:
    - `MODEL_PATH` - The relative path to a local model.
    - `TOKEN_LIMIT` - The `max_new_tokens` to pass to a model.
    - `REQ_PATH` - The relative path to the requirements file.
    - `TEST_PATH` - The relative path to the tests file.
    - `OPENAI_API_KEY` - If using the OpenAI API.
    - `OPENAI_BASE_URL` - If using the OpenAI API.
1. Run one of two scripts:
    - `python -m src.send_data` - To run on a local model.
    Adjust the `session_name` variable to your desired output directory name.
    - `python -m src.send_data_gpt` - To run on OpenAI's GPT. \
    Adjust the `model` variable to your desired model.

The scripts will output files in the `out/{model}/{date}/{time}/` directory.

### Evaluating REST-at From Scripts

Make sure that you're in the correct Python environment before you begin!

1. Follow the steps in [Running REST-at Scripts](#running-rest-at-scripts)
1. Add the following variable to the `.env` file:
    - `MAP_PATH` - The relative path to the alignment file.
1. Run one of two scripts:
    - `python -m src.eval` - To evaluate each REST trace link.
    - `python -m src.label_eval` - To evaluate "is tested" labels.

The script will output an `eval.log` or a `label-eval.log` in `out/{model}/{date}/{time}/` for each model, date, and time, depending on the script used. The file contains key metrics of REST-at, such as accuracy and precision.

The script will also output the following files in the `res/{date}/{time}(-label)` directory:
- `eval.log` - The verbose output of the evaluation.
- `res.log` - All the evaluation results.
- `{model}.log` for each model in `out/` - The average metrics of all runs with the model.
