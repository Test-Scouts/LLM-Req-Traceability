"""
This script converts the GE xlsx files to csv files.
The GE xlsx files are the GE requirements and test steps for AMINA and Diarie.

The GE requirements and test steps for AMINA and Diarie extracted from the files:
- GE_Krav_AMINA.xlsx
- GE_STs_AMINA.xlsx
- GE_Krav_Diarie.xlsx
- GE_STs_Diarie_V2.xlsx

and coverted to csv files:
- GE_Krav_AMINA.csv
- GE_STs_AMINA.csv
- GE_Krav_Diarie.csv
- GE_STs_Diarie_V2.csv

The test case steps for AMINA are separated into multiple columns in the xlsx file.
Therefore, the columns are merge into one column in the csv file and the cells in 
the test steps that don't end with a period are added a period at the end.

"""

import dotenv
import os
import pandas as pd
import argparse
dotenv.load_dotenv()

parser = argparse.ArgumentParser(description="Process file information.")

#Add arguments
parser.add_argument("-n", "--name", dest= "name", type=str, help="Name of the file")
parser.add_argument("-d", "--dir", dest= "directory", type=str, help="Name of the directory")

# Parse arguments
args = parser.parse_args()


merge_from_colum:int = int(os.getenv("MERGE_FROM_COLUMN"))

def get_last_column_with_value(df):
    non_empty_columns = df.columns[df.notna().any()].tolist()
    last_index = df.columns.get_loc(non_empty_columns[-1]) if non_empty_columns else None
    return last_index


#For GE_STs_AMINA, we need to merge the columns for the test steps
def merge_columns(df, start_column:int, end_column:int):
    # Select the columns that need to be merged
    columns_to_merge = df.columns[start_column:end_column]

    # Merge the specified columns into the column at index 2 ('C'), only adding non-empty cells
    # and ensuring each segment ends with a period if it does not already
    df.iloc[:,merge_from_colum ] = df[columns_to_merge].apply(
        lambda row: ' '.join(
            # Add a period to the end of the value if it does not already end with a period
            f"{value}." if not value.endswith('.') else value
            # Iterate over the non-empty cells in the row and convert the values to strings
            # (to avoid issues with NaN values)
            for value in row.dropna().astype(str)
        ),
        # Apply the lambda function to each row in the DataFrame
        # axis=1 specifies that the lambda function should be applied to each row, not each column
        axis=1
    )

    # Drop the now unnecessary columns, except for the column at index 2 ('C')
    df.drop(columns=columns_to_merge[1:], inplace=True)

    return df

# Convert the xlsx file to csv, using 'utf-8' encoding to support swedish special characters
def xlsx_to_csv(path_xlsx, output_csv, should_merge_columns:bool=False):
    df = pd.read_excel(path_xlsx)
    if should_merge_columns:

        # Define the range of columns from 'C' to 'AO' using indices 
        # (this has been manully checked in the xlsx file)
        # 'C' is typically at index 2, since the index for the columns start at 0 (column 'A'). 
        start_column = 2
        end_column = 41

        df = merge_columns(df, start_column, end_column)
        df.to_csv(output_csv, index=False, encoding='utf-8')
    else:
        df.to_csv(output_csv, index=False, encoding='utf-8')

# Load environment variables containing the paths to the GE xlsx files
req_amina = os.getenv("REQ_AMINA")
st_amina = os.getenv("ST_AMINA")
req_diarie = os.getenv("REQ_DIARIE")
st_diarie = os.getenv("ST_DIARIE")

# Define the path to the new GE csv data directory
if args.directory:
    path = f"../src/GE-data-swe/csv/{args.directory}/"
    os.makedirs(path, exist_ok=True)
else:    
    path = "../src/GE-data-swe/csv/"
    os.makedirs(path, exist_ok=True)

# Define the mappings of csv names to xlsx paths
file_mappings = {
    "GE_Krav_AMINA": req_amina,
    "GE_STs_AMINA": st_amina,
    "GE_Krav_Diarie": req_diarie,
    "GE_STs_Diarie_V2": st_diarie
}

# Convert the xlsx files to csv
for name, xlsx_path in file_mappings.items():
    if args.name:
    # Define the path to the new csv file
        file_path =f'{path}{name}{args.name}.csv'
    else:
    # Define the path to the new csv file
        file_path =f'{path}{name}.csv'
    print(f'file path: {file_path}')
    # For GE_STs_AMINA, merge the columns for the test steps
    if name =="GE_STs_AMINA":
        xlsx_to_csv(xlsx_path, file_path, True) # merge_columns=True
    else:
        xlsx_to_csv(xlsx_path, file_path)

print("Conversion of GE xlsx files to csv files completed successfully.")