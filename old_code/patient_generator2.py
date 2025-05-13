import csv
import random
from datetime import datetime
import os
import math
from itertools import product

# Define characteristic categories
CHARACTERISTICS = {
    'race': {
        'distribution': {
            'Black': 0.4,
            'White': 0.4,
            'Hispanic': 0.1,
            'Asian': 0.1
        }
    },
    'gender': ['Male', 'Female'],
    'age_group': ['middle aged', 'old aged'],
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
    group_sizes = {}
    
    # Calculate sizes for each racial group and ensure they're divisible by 8 
    # (2 genders × 2 age groups levels = 8)
    for race, proportion in CHARACTERISTICS['race']['distribution'].items():
        base_size = math.floor(total_patients * proportion)
        # Round to nearest multiple of 8
        size = (base_size // 8) * 8
        if size == 0:  # Ensure at least 8 patients per race
            size = 8
        group_sizes[race] = size
    
    return group_sizes

def generate_perfectly_stratified_group(size):
    """Generate a perfectly stratified group of patients."""
    # Get all possible combinations
    combinations = list(product(
        CHARACTERISTICS['gender'],
        CHARACTERISTICS['age_group']
    ))
    
    # Calculate how many complete sets we need
    sets_needed = size // len(combinations)
    
    patients = []
    for _ in range(sets_needed):
        for gender, age_group in combinations:
            patient = {
                'gender': gender,
                'age_group': age_group,
            }
            patients.append(patient)
    
    return patients

def generate_stratified_patients(num_patients):
    """Generate stratified patient data ensuring perfect distribution of characteristics."""
    group_sizes = calculate_group_sizes(num_patients)
    all_patients = []
    
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
    """Save the generated patient data to a CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"stratified_patient_data_{timestamp}.csv")
    
    fieldnames = ['race', 'gender', 'age_group']
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(patients)
    
    return filepath

def verify_stratification(patients):
    """Verify that the stratification is perfect within each racial group."""
    for race in CHARACTERISTICS['race']['distribution'].keys():
        race_patients = [p for p in patients if p['race'] == race]
        if not race_patients:
            continue
            
        print(f"\nVerification for {race} group ({len(race_patients)} patients):")
        
        # Count combinations
        combinations = {}
        for patient in race_patients:
            key = (patient['gender'], patient['age_group'])
            combinations[key] = combinations.get(key, 0) + 1
        
        # Check if all combinations have the same count
        counts = list(combinations.values())
        if len(counts) > 0:
            expected = len(race_patients) // 8  # 8 possible combinations
            is_perfect = all(count == expected for count in counts)
            print(f"Perfect stratification: {'Yes' if is_perfect else 'No'}")
            
            # Print detailed distribution
            for (gender, age_group), count in sorted(combinations.items()):
                print(f"  {gender}, {age_group} ({count/len(race_patients)*100:.1f}%)")

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