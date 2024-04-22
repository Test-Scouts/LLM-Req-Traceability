import pandas as pd

# Create a DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': ['30', '25', '35'],
    'Location': ['New York', 'Los Angeles', 'Chicago']
}

# Create a DataFrame
data2 = {
    'Name': ['New: Alice', 'Bob', 'New: Charlie'],
    'Age': ['30', '25', '35'],
    'Location': ['New York', 'Los Angeles', 'Chicago']
}

r_df = pd.DataFrame(data)
st_df = pd.DataFrame(data2)

print("Original DataFrame:",r_df)
print("\n\n")
def process_value(value):
    # Perform some processing on the value
    return f"New: {value}"

# Iterate over each cell in the DataFrame and update it
for column in r_df.columns:
    for index in r_df.index:
        original_value = r_df.at[index, column]
        new_value = process_value(original_value)
        r_df.at[index, column] = new_value


print(r_df)
print("\n\n")


req_ex = r_df['Name'].unique()

filtered_st_ex = st_df[st_df['Name'].isin(req_ex)]


filtered_st_ex.to_csv("filtered_st_csv.csv", index=False)

print(filtered_st_ex)