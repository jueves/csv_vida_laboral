# Vida Laboral PDF to CSV Converter

Converts Spanish Government Seguridad Social PDF reports on vida laboral to CSV format. Extracts employment history tables from multi-page PDFs and processes them into structured CSV data.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pdf_to_csv.py archivo.pdf
```

This will generate an `archivo.csv` file in the same directory.

## Features

- **Multi-page processing**: Extracts tables from all pages (excluding the first page)
- **Smart table validation**: Only processes tables containing "SITUACIÓN/ES" in the first row
- **Automatic row reconstruction**: Uses the DÍAS column to identify and combine split rows
- **Manual headers**: Applies standardized column names for consistency
- **CSV output**: Generates clean, structured CSV files ready for filtering and analysis

## Output Columns

The generated CSV contains the following columns:
- RÉGIMEN
- ID EMPRESA
- NOMBRE EMPRESA
- FECHA ALTA
- FECHA DE EFECTO DE ALTA
- FECHA DE BAJA
- C.T.
- CTP %
- G.C.
- DÍAS

## Dependencies

- `camelot-py`: For PDF table extraction using stream method
- `pandas`: For data manipulation and CSV export
