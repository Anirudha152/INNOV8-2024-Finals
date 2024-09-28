import csv


def convert_txt_to_csv(txt_file, csv_file):
    with open(txt_file, 'r') as infile, open(csv_file, 'w', newline='') as outfile:
        reader = infile.readlines()
        writer = csv.writer(outfile)

        # Write the header
        writer.writerow(['Index', 'RiskFactor', 'VacancyFactor', 'Flag', 'BigFlag'])

        # Write the data
        for line in reader:
            data = line.split()
            writer.writerow(data)


# Convert final.txt to final.csv
convert_txt_to_csv('final.txt', 'final.csv')