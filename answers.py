import json
from collections import defaultdict
from datetime import datetime, timedelta


def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_output_to_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def save_people_compt_to_json(people_with_compt, compt_list, year, output_file):
    data = {
        'fiscal_year': year,
        'completions': compt_list,
        'people': people_with_compt
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


# List each completed training with a count of how many people have completed that training.

def count_completions(people):
    compt_counts = defaultdict(int)  

    for person in people:
        unique_completions = set()  
        for completion in person['completions']:
            compt_name = completion['name']
            if compt_name not in unique_completions:
                compt_counts[compt_name] += 1
                unique_completions.add(compt_name)
    return compt_counts





# Given a list of trainings and a fiscal year (defined as 7/1/n-1 – 6/30/n), for each specified training, list all people that completed that training in the specified fiscal year.

def is_within_fiscal_year(date_str, fiscal_year_start, fiscal_year_end):
    date_format = "%m/%d/%Y" 
    date_obj = datetime.strptime(date_str, date_format)
    return fiscal_year_start <= date_obj <= fiscal_year_end


def get_fiscal_year_range(year):
    fiscal_year_start = datetime(int(year) - 1, 7, 1)  
    fiscal_year_end = datetime(int(year), 6, 30)      
    return fiscal_year_start, fiscal_year_end


def get_people_by_trainings_and_fiscal_year(people, comp_list, year):
    fiscal_year_start, fiscal_year_end = get_fiscal_year_range(year)
    people_with_comps = []

    for person in people:
        for comp in person['completions']:
            comp_name = comp['name']
            timestamp = comp['timestamp']
            
            if comp_name in comp_list and is_within_fiscal_year(timestamp, fiscal_year_start, fiscal_year_end):
                people_with_comps.append(person['name'])
                break

    return people_with_comps

# Given a date, find all people that have any completed trainings that have already expired, 
# or will expire within one month of the specified date (A training is considered expired the day after its expiration date). 
# For each person found, list each completed training that met the previous criteria, with an additional field to indicate expired vs expires soon.

def check_expiration_status(expiration_date_str, date_given):
    date_format = "%m/%d/%Y"
    expiration_date = datetime.strptime(expiration_date_str, date_format)
    
    expires_soon_threshold = date_given + timedelta(days=30)
    
    if date_given > expiration_date:
        return 'expired'
    elif date_given <= expiration_date <= expires_soon_threshold:
        return 'expiring soon'
    else:
        return None


def get_expiring_completions(people, current_date_str):
    current_date = datetime.strptime(current_date_str, "%m/%d/%Y")
    result = []

    for person in people:
        person_data = {
            'name': person['name'],
            'completions': []
        }

        for comp in person['completions']:
            comp_name = comp['name']
            timestamp = comp['timestamp']
            expires_date = comp.get('expires')

            if expires_date:
                expiration_status = check_expiration_status(expires_date, current_date)
                if expiration_status:  
                    comp_info = {
                        'name': comp_name,
                        'timestamp': timestamp,
                        'expiration_status': expiration_status,
                        'expires': expires_date
                    }
                    person_data['completions'].append(comp_info)
        
        if person_data['completions']:
            result.append(person_data)

    return result


    
def main():
    
    file_path = 'trainings.json'
    people = load_json_file(file_path)
    
    # 1
    comp_counts = count_completions(people)
    output_file = 'completed_training_counts.json'
    save_output_to_json(comp_counts, output_file)

    # 2
    test_training_list = ['Electrical Safety for Labs', 'X-Ray Safety', 'Laboratory Safety Training']
    test_year = '2024'
    people_with_comps = get_people_by_trainings_and_fiscal_year(people, test_training_list, test_year)
    output_file = 'people_by_trainings_fiscal_year.json'
    save_people_compt_to_json(people_with_comps, test_training_list, test_year, output_file)

    # 3
    test_date = '10/01/2023'  
    expiring_training_status = get_expiring_completions(people, test_date)
    output_file = 'expiring_trainings.json'
    save_output_to_json(expiring_training_status, output_file)
    

if __name__=="__main__":
    main()