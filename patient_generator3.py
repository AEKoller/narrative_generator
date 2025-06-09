import csv
import random
from datetime import datetime
import os
import math
from itertools import product

# We start by defining the characteristics of the patients we want to generate.
# Race is nested within a dictionary so that we can have both the race as the key
# and the distribution as a value. This allows us to easily adjust the proportions
# Race will also be our primary stratification variable, as we want to ensure that each
# racial group has an equal representation of all other characteristics.
CHARACTERISTICS = {
    'race': {
        'distribution': {
            'Black': 0.25,
            'White': 0.25,
            'Hispanic': 0.25,
            'Asian': 0.25
        }
    },
    'gender': ['Male', 'Female'],
    'age_group': ['middle aged', 'old aged'],
    'pain_intensity': ['moderate', 'high'],
}

def calculate_group_sizes(total_patients):
    """
    Calculate the number of patients for each racial group. Groups are defined by race
    because each race needs an equal stratification of all characteristics 

    Args:
        total_patients: integer indicating number of patients to generate
    Returns:
        group_sizes: integer indicating size of group given relative to num. of patients
    """
    # We start by initializing an empty dictionary to hold the sizes of each group.
    group_sizes = {}
    
    # Because we have 4 racial groups, and for each racial group there are 2 genders
    # we need to set a base size for each racial group that is divisible by 8 
    # We start a for loop to iterate through each racial group and its proportion
    # in the CHARACTERISTICS dictionary
    for race, proportion in CHARACTERISTICS['race']['distribution'].items():
        # We calculate the base size for each racial group by multiplying the total number
        # of patients by the proportion of that racial group
        # We use math.floor to ensure that we round down to the nearest whole number
        base_size = math.floor(total_patients * proportion)
        # We then round the base size to the nearest multiple of 8
        size = (base_size // 8) * 8
        if size == 0:  # Ensure at least 8 patients per race
            size = 8
        group_sizes[race] = size
    
    return group_sizes

def generate_perfectly_stratified_group(size):
    """
    Generate a perfectly stratified group of patients.
    Args:
        size: integer indicating the number of patients to generate for this group
    Returns:
        patients: list of dictionaries, each representing a patient with stratified characteristics
    """
    # Get all possible combinations
    combinations = list(product(
        CHARACTERISTICS['gender'],
        CHARACTERISTICS['age_group'],
        CHARACTERISTICS['pain_intensity']
    ))
    
    # Calculate how many complete sets we need
    sets_needed = size // len(combinations)
    
    # We initialize an empty list to hold the patients
    patients = []
    # We then iterate through the number of sets needed, and for each set, we create
    for _ in range(sets_needed):
        # For each combination of characteristics, we create a patient dictionary
        for gender, age_group, pain_intensity in combinations:
            # Create a patient dictionary with the current combination of characteristics
            patient = {
                'gender': gender,
                'age_group': age_group,
                'pain_intensity': pain_intensity,
            }
            patients.append(patient)
    
    return patients

def generate_stratified_patients(num_patients):
    """
    Generate stratified patient data ensuring perfect distribution of characteristics.
    Args:
        num_patients: integer indicating the total number of patients to generate
    Returns:
        all_patients: list of dictionaries, each representing a patient with stratified characteristics
    """
    
    # First, we calculate the sizes of each racial group based on the total number of patients
    group_sizes = calculate_group_sizes(num_patients)
    # We initialize an empty list to hold all patients
    all_patients = []
    
    # We then iterate through each racial group and its size
    # For each racial group, we generate a perfectly stratified group of patients
    for race, size in group_sizes.items():
        # Generate perfectly stratified group
        race_patients = generate_perfectly_stratified_group(size)
        
        # Add race to each patient
        for patient in race_patients:
            patient['race'] = race
        
        # Shuffle the patients for this racial group
        random.shuffle(race_patients)
        all_patients.extend(race_patients)
    
    # Shuffle all patients while maintaining stratification
    random.shuffle(all_patients)
    
    return all_patients

def save_patients_to_csv(patients, output_dir="patient_data"):
    """
    Save the generated patient data to a CSV file.
    Args:
        patients: list of dictionaries, each representing a patient with stratified characteristics
        output_dir: directory where the CSV file will be saved
    Returns:
        filepath: string indicating the path to the saved CSV file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    # We also create a timestamp for the filename to ensure uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # We then create the filepath for the CSV file
    filepath = os.path.join(output_dir, f"stratified_patient_data_{timestamp}.csv")
    
    # We set the column names for the CSV file as the characteristics we want to include
    fieldnames = ['race', 'gender', 'age_group', 'pain_intensity']
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(patients)
    
    return filepath

def verify_stratification(patients):
    """
    Verify that the stratification is perfect within each racial group.
    Args:
        patients: list of dictionaries, each representing a patient with stratified characteristics
    Returns:
        Print verification results for each racial group
    """
    for race in CHARACTERISTICS['race']['distribution'].keys():
        race_patients = [p for p in patients if p['race'] == race]
        if not race_patients:
            continue
            
        print(f"\nVerification for {race} group ({len(race_patients)} patients):")
        
        # Count combinations
        combinations = {}
        for patient in race_patients:
            key = (patient['gender'], patient['age_group'], patient['pain_intensity'])
            combinations[key] = combinations.get(key, 0) + 1
        
        # Check if all combinations have the same count
        counts = list(combinations.values())
        if len(counts) > 0:
            expected = len(race_patients) // 8  # 8 possible combinations
            is_perfect = all(count == expected for count in counts)
            print(f"Perfect stratification: {'Yes' if is_perfect else 'No'}")
            
            # Print detailed distribution
            for (gender, age_group, pain_intensity), count in sorted(combinations.items()):
                print(f"  {gender}, {age_group}, {pain_intensity} ({count/len(race_patients)*100:.1f}%)")

def main():
    while True:
        try:
            num_patients = int(input("Enter the number of patients to generate: "))
            if num_patients <= 0:
                print("Please enter a positive number.")
                continue
            if num_patients < 32:  # Minimum to ensure stratification (8 combinations × 4 races)
                print("Please enter at least 32 patients to ensure proper stratification.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Generate and save patients
    patients = generate_stratified_patients(num_patients)
    output_file = save_patients_to_csv(patients)
    
    # Print summary statistics
    print(f"\nGenerated {len(patients)} patients and saved to {output_file}")
    
    # Verify and print stratification statistics
    verify_stratification(patients)
    
    # Print overall racial distribution
    print("\nOverall Racial Distribution:")
    for race in CHARACTERISTICS['race']['distribution'].keys():
        race_count = sum(1 for p in patients if p['race'] == race)
        print(f"{race}: {race_count} patients ({race_count/len(patients)*100:.1f}%)")

if __name__ == "__main__":
    main()