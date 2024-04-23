import pandas as pd

def print_info_AMINA_requirements_and_tests(req_df: pd.DataFrame, st_df: pd.DataFrame, detailed: bool = False):
    # Calculate totals
    total_requirements = len(req_df)
    total_tests = len(st_df)

    ###############################
    # Calculate not tested
    ###############################
    # Find test cases where Beskrivning is empty or NaN
    empty_test_cases = st_df[st_df['Beskrivning'].isnull() | (st_df['Beskrivning'] == '')]

    # Extracting unique IDs from both DataFrames
    unique_req_ids = set(req_df['GE_KravID'].dropna().unique())
    unique_st_ids = set(st_df['GE_KravID'].dropna().unique())

    # Finding IDs in req_df that are not in st_df
    unmatched_ids = unique_req_ids.difference(unique_st_ids)

    # Count of unmatched IDs
    unmatched_count = len(unmatched_ids)
    total_not_tested = len(empty_test_cases) + unmatched_count

    # Find IDs in st_df that are not in req_df
    unmatched_ids = unique_st_ids.difference(unique_req_ids)

    # Filter st_df for rows where GE_KravID is in unmatched IDs
    unmatched_tests = st_df[st_df['GE_KravID'].isin(unmatched_ids)]

    ###############################
    # Calculate 1:M and 1:1
    ###############################
    # Merge the data frames on GE_KravID
    merged_df = pd.merge(req_df, st_df, on='GE_KravID', how='inner')

    # Group by GE_KravID in the merged DataFrame and count the number of tests for each requirement
    test_counts = merged_df.groupby('GE_KravID').size()

    # Filter to get only those GE_KravID with more than one test
    multi_test_reqs = test_counts[test_counts > 1].index

    # Extract rows from req_df where GE_KravID is in the list of IDs with more than one test
    one_to_many = req_df[req_df['GE_KravID'].isin(multi_test_reqs)]

    # Filter to get only those GE_KravID with exactly one test
    one_to_one_reqs = test_counts[test_counts == 1].index

    # Extract rows from req_df where GE_KravID has a 1:1 relationship with st_df
    one_to_one = req_df[req_df['GE_KravID'].isin(one_to_one_reqs)]

    #####################################
    # Calculate ST with Nan RE_ID values
    #####################################
    st_with_nan_kravid = st_df[st_df['GE_KravID'].isna()]

    # Compile results into a DataFrame for display
    results_df = pd.DataFrame({
        "Total Requirements": [total_requirements],
        "Total Tests": [total_tests],
        "RE Not Tested": [total_not_tested],
        "RE with Multiple Tests(1:M)": [len(one_to_many)],
        "RE with One Test(1:1)": [len(one_to_one)],
        "ST with Nan RE_ID": [len(st_with_nan_kravid)],
        "ST with RE but not found in RE file": [len(unmatched_tests)]
    })

    print(results_df)
    print("""

    """)
    if detailed:
        print("Details of requirements with multiple tests:")
        print(one_to_many)
        print("\n")
        print("Details of requirements with no tests:")
        print(empty_test_cases.to_string(index=False))
        print("\n\n")

