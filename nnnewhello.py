import re
import json
import os

timeline = []
max_date = '00-0000'
index_max_date = 0

def parse_timeline(file_name):
    global timeline
    with open(file_name, 'r') as file:
        lines = file.readlines()
        in_timeline = False
        for line in lines:
            if line.strip() == '## Timeline:':
                in_timeline = True
            elif in_timeline and line.strip() == '':
                break
            elif in_timeline:
                match = re.match(r'-\s*(\w+)\s*::\s*(\d{2}-\d{4}\s*--\s*\d{2}-\d{4}|\d{2}-\d{4}\s*--\s*CURRENT|\d{2}-\d{4})\s*::\s*(.*)\s*::\s*(\w+)', line)
                if match:
                    date_range = match.group(2).split('--')
                    entry = {
                        'type': match.group(1).strip(),
                        'start_date': date_range[0].strip(),
                        'end_date': date_range[1].strip() if len(date_range) > 1 else 'CURRENT',
                        'text': match.group(3).strip(),
                        'severity': match.group(4).strip()
                    }
                    timeline.append(entry)

def calculate_factor(file_index):
    global max_date
    global index_max_date
    job_map = {}
    education_map = {}
    jobeducation_map = {}
    latest_education_year = '0000'
    for entry in timeline:
        if entry['type'] == "JOB":
            start_date = entry['start_date']
            # if start_date != 'CURRENT':
            #     if start_date > max_date:
            #         max_date = start_date
            #         index_max_date = file_index
            if start_date == 'CURRENT':
                start_date = '12-2017'
            start_month, start_year = start_date.split('-')
            if start_month >= '07':
                start_year = str(int(start_year) + 1)

            end_date = entry['end_date']
            # if end_date != 'CURRENT':
            #     if end_date > max_date:
            #         max_date = end_date
            #         index_max_date = file_index
            if end_date == 'CURRENT':
                end_date = '12-2017'
            end_month, end_year = end_date.split('-')
            if end_month >= '07':
                end_year = str(int(end_year) + 1)

            if start_date == '00-0000' and end_date == '00-0000':
                start_date = '01-2014'
                end_date = '01-2012'
                start_month, start_year = start_date.split('-')

            if start_date == '00-0000':
                start_date = str(int(end_month)) + '-' + str(int(end_year) - 4)
                start_month, start_year = start_date.split('-')

            if end_date == '00-0000':
                end_date = str(int(start_month)) + '-' + str(int(start_year) + 4)
                end_month, end_year = end_date.split('-')

            for year in range(int(start_year), int(end_year) + 1):
                if year not in job_map:
                    job_map[year] = 0
                job_map[year] += 1

            if start_date > max_date:
                max_date = start_date
                index_max_date = file_index

            if end_date > max_date:
                max_date = end_date
                index_max_date = file_index


            for year in range(int(start_year), int(end_year) + 1):
                if year not in jobeducation_map:
                    jobeducation_map[year] = 0
                jobeducation_map[year] += 1
        elif entry['type'] == "EDU":
            start_date = entry['start_date']
            # if start_date != 'CURRENT':
            #     if start_date > max_date:
            #         max_date = start_date
            #         index_max_date = file_index
            if start_date == 'CURRENT':
                start_date = '12-2017'
            start_month, start_year = start_date.split('-')
            if start_month >= '07':
                start_year = str(int(start_year) + 1)

            end_date = entry['end_date']
            # if end_date != 'CURRENT':
            #     if end_date > max_date:
            #         max_date = end_date
            #         index_max_date = file_index
            if end_date == 'CURRENT':
                end_date = '12-2017'
            end_month, end_year = end_date.split('-')
            if end_month >= '07':
                end_year = str(int(end_year) + 1)

            if start_date == '00-0000' and end_date == '00-0000':
                start_date = '01-2014'
                end_date = '01-2012'
                start_month, start_year = start_date.split('-')
                end_month, end_year = end_date.split('-')

            if start_date == '00-0000' and end_date != '00-0000':
                #end_date = start_date - 2 years
                start_date = str(int(end_month)) + '-' + str(int(end_year) - 2)
                start_month, start_year = start_date.split('-')
                end_month, end_year = end_date.split('-')

            if end_date == '00-0000' and start_date != '00-0000':
                end_date = start_date;
                #start_date = end_date - 2 years
                end_month, end_year = end_date.split('-')
                start_date = str(int(end_month)) + '-' + str(int(end_year) - 2)
                start_month, start_year = start_date.split('-')
                end_month, end_year = end_date.split('-')

            if start_date > max_date:
                max_date = start_date
                index_max_date = file_index

            if end_date > max_date:
                max_date = end_date
                index_max_date = file_index


            for year in range(int(start_year), int(end_year) + 1):
                if year not in education_map:
                    education_map[year] = 0
                education_map[year] += 1
            for year in range(int(start_year), int(end_year) + 1):
                if year not in jobeducation_map:
                    jobeducation_map[year] = 0
                jobeducation_map[year] += 1

            latest_education_year = max(latest_education_year, end_year)

    sumjobs = 0
    sumeducation = 0
    sumjobeducation = 0
    for key in job_map:
        sumjobs += job_map[key]
    for key in education_map:
        sumeducation += education_map[key]
    for key in jobeducation_map:
        sumjobeducation += jobeducation_map[key]

    factor1 = sumjobs / len(job_map) if len(job_map) > 0 else 1
    factor2 = sumeducation / len(education_map) if len(education_map) > 0 else 1
    factor3 = sumjobeducation / len(jobeducation_map) if len(jobeducation_map) > 0 else 1
    factor = factor1 * factor2 * factor3

    flag = 0
    bigflag = 0
    for entry in timeline:
        if entry['type'] == "JOB" and entry['severity'] == 'HIGH':
            start_date = entry['start_date']
            if start_date == 'CURRENT':
                start_date = '12-2017'
            start_month, start_year = start_date.split('-')
            if start_month >= '07':
                start_year = str(int(start_year) + 1)

            end_date = entry['end_date']
            if end_date == 'CURRENT':
                end_date = '12-2017'
            end_month, end_year = end_date.split('-')
            if end_month >= '07':
                end_year = str(int(end_year) + 1)

            if int(start_year) == int(latest_education_year) or int(start_year) == int(latest_education_year) + 1:
                flag = 1

    for entry in timeline:
        if entry['type'] == "EDU":
            start_date = entry['start_date']
            if start_date == 'CURRENT':
                start_date = '12-2017'
            start_month, start_year = start_date.split('-')
            if start_month >= '07':
                start_year = str(int(start_year) + 1)

            end_date = entry['end_date']
            if end_date == 'CURRENT':
                end_date = '12-2017'
            end_month, end_year = end_date.split('-')
            if end_month >= '07':
                end_year = str(int(end_year) + 1)

            for entry2 in timeline:
                if entry2['type'] == "JOB" and entry2['severity'] == 'HIGH':
                    start_date = entry2['start_date']
                    if start_date == 'CURRENT':
                        start_date = '12-2017'
                    start_month, start_year = start_date.split('-')
                    if start_month >= '07':
                        start_year = str(int(start_year) + 1)

                    end_date = entry2['end_date']
                    if end_date == 'CURRENT':
                        end_date = '12-2017'
                    end_month, end_year = end_date.split('-')
                    if end_month >= '07':
                        end_year = str(int(end_year) + 1)

                    if int(start_year) == int(end_year) or int(start_year) == int(end_year) + 1:
                        bigflag = 1
    if len(job_map) == 0:
        return factor, 1, flag, bigflag
    vacancies = 0
    first_year = min(job_map.keys())
    last_year = max(job_map.keys())
    for year in range(first_year, last_year + 1):
        if year not in jobeducation_map:
            vacancies += 1
    vacancy_factor = 1 + vacancies / len(job_map) if len(job_map) > 0 else 1

    return factor, vacancy_factor, flag, bigflag

def count_flag(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            _, _, _, flag, _ = line.split()
            if flag == '1':
                count += 1
        return count

def count_bigflag(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            _, _, _, _, bigflag = line.split()
            if bigflag == '1':
                count += 1
        return count

def main():
    output_folder = 'outputs'
    final_factors = {}
    for i in range(1000):
        file_name = os.path.join(output_folder, f'output{i}.txt')
        if os.path.exists(file_name):
            global timeline
            timeline = []
            parse_timeline(file_name)
            factor, vacancy_factor, flag, bigflag = calculate_factor(i)
            final_factors[i] = factor, vacancy_factor, flag, bigflag

    with open('final.txt', 'w') as final_file:
        for i, factor in final_factors.items():
            final_file.write(f'{i} {factor[0]:.4f} {factor[1]:.4f} {factor[2]} {factor[3]}\n')

    print(count_flag('final.txt'))
    print(count_bigflag('final.txt'))
    print(max_date)
    print(index_max_date)

if __name__ == "__main__":
    main()