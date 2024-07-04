import openpyxl

def xlsx_to_txt(input_file, output_file):
    # Load the Excel workbook
    workbook = openpyxl.load_workbook(input_file)
    sheet = workbook.active

    # Open a text file for writing
    with open(output_file, 'w') as txt_file:
        # Iterate through rows and columns to read data
        for row in sheet.iter_rows(values_only=True):
            # Convert each row to a string
            row_str = '\t'.join(str(cell) for cell in row if cell is not None)
            # Write the row string to the text file
            txt_file.write(row_str + '\n')

    # Close the workbook after reading
    workbook.close()

# Example usage
if __name__ == "__main__":
    input_excel = 'mapa.xlsx'
    output_text = 'mapa.txt'
    xlsx_to_txt(input_excel, output_text)
