#!/usr/bin/env python3
"""
Converts Spanish Government Seguridad Social PDF reports on vida laboral to CSV format.
Extracts employment history tables from multi-page PDFs and processes them into structured CSV data.
"""

import camelot
import pandas as pd
import sys
import os
import re

# Manual headers as constant
MANUAL_HEADERS = [
    "RÉGIMEN", "ID EMPRESA", "NOMBRE EMPRESA", "FECHA ALTA",
    "FECHA DE EFECTO DE ALTA", "FECHA DE BAJA", "C.T.", "CTP %", "G.C.", "DÍAS"
]

def is_valid_table(table_df):
    """Checks if table contains 'SITUACIÓN/ES' in the first row."""
    if table_df.empty:
        return False
    
    first_row_text = ' '.join(str(cell).strip() for cell in table_df.iloc[0] if pd.notna(cell))
    return bool(re.search(r'\bSITUACIÓN/ES\b', first_row_text, re.IGNORECASE))

def has_dias_value(row):
    """Checks if a row has a valid DÍAS value."""
    dias_value = row["DÍAS"]
    return dias_value and str(dias_value).strip() and str(dias_value).strip() != 'nan'

def process_table(table_df):
    """Processes a table by removing the first 6 rows and reconstructing rows."""
    # Remove first 6 rows and apply headers
    df = table_df.iloc[6:].copy()
    df.columns = MANUAL_HEADERS
    
    # Reconstruct rows using DÍAS as indicator
    real_rows = []
    current_row = None
    
    for i, row in df.iterrows():
        if has_dias_value(row):
            if current_row is not None:
                real_rows.append(current_row)
            current_row = row.tolist()
        else:
            if current_row is not None:
                # Concatenate with previous row
                for j, cell_value in enumerate(row):
                    if cell_value and str(cell_value).strip() and str(cell_value).strip() != 'nan':
                        if current_row[j]:
                            current_row[j] = f"{current_row[j]} {cell_value}".strip()
                        else:
                            current_row[j] = str(cell_value)
    
    if current_row is not None:
        real_rows.append(current_row)
    
    return pd.DataFrame(real_rows, columns=MANUAL_HEADERS)

def extract_tables_from_pdf(pdf_path):
    """Extracts all tables and processes only the valid ones."""
    print(f"Processing: {pdf_path}")
    
    try:
        # Read all tables at once
        tables = camelot.read_pdf(pdf_path, pages='2-end', flavor='stream')
        
        if not tables:
            print("No tables found")
            return None
        
        print(f"Found {len(tables)} tables in total")
        
        # Filter only valid tables
        valid_tables = []
        for table in tables:
            if is_valid_table(table.df):
                valid_tables.append(table)
                print(f"Valid table found on page {table.page}")
        
        if not valid_tables:
            print("No valid tables found")
            return None
        
        print(f"Processing {len(valid_tables)} valid tables...")
        
        # Process all valid tables
        processed_tables = []
        for table in valid_tables:
            processed_df = process_table(table.df)
            if not processed_df.empty:
                processed_tables.append(processed_df)
                print(f"Page {table.page}: {processed_df.shape[0]} rows processed")
        
        if not processed_tables:
            print("Could not process valid tables")
            return None
        
        # Concatenate all processed tables
        final_df = pd.concat(processed_tables, ignore_index=True)
        print(f"Total: {final_df.shape[0]} rows in {len(processed_tables)} tables")
        
        return final_df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_csv_optimized.py <file.pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} does not exist")
        sys.exit(1)
    
    # Process PDF
    table = extract_tables_from_pdf(pdf_path)
    
    if table is not None:
        # Save CSV
        output_path = pdf_path.replace('.pdf', '.csv')
        table.to_csv(output_path, index=False, encoding='utf-8')
        print(f"CSV saved: {output_path}")
    else:
        print("Could not process PDF")

if __name__ == "__main__":
    main()
