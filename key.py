import csv
import os
import ahocorasick

def build_automaton(keywords):
    A = ahocorasick.Automaton()
    for idx, keyword in enumerate(keywords):
        A.add_word(keyword, (idx, keyword))
    A.make_automaton()
    return A

def extract_rows_by_keywords(input_csv_file, keyword_file, output_csv_file):
    # Read the keywords from the keyword file and convert to lowercase
    with open(keyword_file, 'r', encoding='utf-8') as keyword_file:
        keywords = {keyword.strip().lower() for keyword in keyword_file}

    # Build Aho-Corasick automaton for efficient multi-keyword matching
    automaton = build_automaton(keywords)

    # Initialize a set to store the unique matching rows
    matching_rows = set()

    # Read the input CSV file and extract rows based on keywords
    with open(input_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Only consider the first column for exact matching
            if row and row[0].lower() in keywords:
                matching_rows.add(tuple(row))

    # Write the unique matching rows to the output CSV file
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in matching_rows:
            writer.writerow(row)

# Example usage
input_csv_file = os.path.join('.', 'dif_result.csv')  # Replace with your input CSV file path
keyword_file = os.path.join('.', 'key.txt')  # Replace with your keyword file path
output_csv_file = os.path.join('.', 'matching_results.csv')  # Replace with the desired output CSV file path

# Extract rows by keywords and create a single CSV file for all unique matching rows
extract_rows_by_keywords(input_csv_file, keyword_file, output_csv_file)
