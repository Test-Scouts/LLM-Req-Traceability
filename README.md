# LLM-Req-Traceability

This repository is dedicated for Bao's &amp; Nicole's thesis work.


## Running Scripts

Scripts should be run as modules to ensure that the relative imports work. E.g.:
```bash
$ python -m <path.to.module> # Omit the -.py file name extension
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
