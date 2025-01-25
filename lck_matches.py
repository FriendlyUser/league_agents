import pandas as pd

# Define the path to the CSV file
csv_file = '2025_LoL_esports_match_data_from_OraclesElixir.csv'

try:
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    print(f"Successfully loaded '{csv_file}'.")
except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found.")
    # exit(1)
except pd.errors.EmptyDataError:
    print(f"Error: The file '{csv_file}' is empty.")
    # exit(1)
except pd.errors.ParserError:
    print(f"Error: The file '{csv_file}' does not appear to be in CSV format or is corrupted.")
    # exit(1)

# Display the first few rows to understand the data structure (optional)
print("\nFirst 5 rows of the dataset:")
print(df.head())

# Check if the 'league' column exists
if 'league' not in df.columns:
    print("Error: The 'league' column does not exist in the dataset.")
    exit(1)

# Filter the DataFrame for rows where the 'league' column is 'LCK'
lck_matches = df[df['league'] == 'LCK']

# Check if any matches were found
if lck_matches.empty:
    print("\nNo matches found for the LCK league.")
else:
    print(f"\nNumber of LCK matches found: {len(lck_matches)}")
    # Optionally, display the filtered data
    print(lck_matches)

    # Save the filtered data to a new CSV file (optional)
    output_file = 'LCK_matches.csv'
    lck_matches.to_csv(output_file, index=False)
    print(f"\nFiltered LCK matches have been saved to '{output_file}'.")
