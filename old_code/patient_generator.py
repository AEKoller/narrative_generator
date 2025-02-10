import csv
import random
from faker import Faker
from datetime import datetime
import os

# Output CSV file will have a timestamp attached to it
folder_path = "patient_data"
os.makedirs(folder_path, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE_PATH = os.path.join(folder_path, f"patient_data_experimental_{timestamp}.csv")

# /////////////////////////////////////////////////////////////////////////////
# >>>>>>>>>>>>>>>HOW MANY RECORDS WOULD YOU LIKE TO GENERATE?<<<<<<<<<<<<<<<<<<
NUM_RECORDS = 10
# /////////////////////////////////////////////////////////////////////////////

# All possible values for patients

# 20240821 Considering only cancer statistics. Will have to add weights based on demographic data
# https://cookcountyhealthatlas.org/change-institute-cancer


LOCATIONS = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"
]
ILLNESSES = [
    "pancreatic cancer", "lung cancer", "brain tumor", "ALS", "Alzheimer's",
    "Parkinson's", "multiple sclerosis", "heart failure", "COPD",
    "end-stage renal disease", "depression"
]

# Will more than likely omit mental states 
MENTAL_STATES = ["mentally capable", "not mentally capable"]

# Need to add subtelty to the mentioning of pain 
PAIN_TYPES = [
    "severe physical pain", "severe mental pain",
    "both physical and mental pain"
]

# Make a list between 1 and 12+ months with each month being represented. This is a rough estimation make by a medical professional. 
# Will need to add realisitc prognoses for specific cancers by adding weights 
PROGNOSES1 = ["less than 1 month", "2 months", "3 months", "4 months", "5 months", 
             "6 months", "7 months", "8 months", "9 months", "10 months", "11 months", 
             "12 months", "12+ months"]
PROGNOSES = [
    "less than 1 month", "1-3 months", "3-6 months", "6-12 months",
    "1-2 years", "2-5 years"
]

# Experimental Variables 

# Literacy made need more training outside of simple instruction
LITERACY = [
    "7th grade level", "8th grade level", "9th grade level", "10th grade level", "11th grade level", "12th grade level", "Freshman in college", "Sophomore in college", "Junior in college", "Senior in college"
]
JOB_STATUS = [
    "Able to work", "Unable to work"
]


# Initialize the Faker library for fake names
fake = Faker()

# Generate random patient data and write it to the CSV file
with open(CSV_FILE_PATH, "w", newline="") as csv_file:
    fieldnames = [
        "first name", "last name", "age", "gender", "location", "illness", "mental_state",
        "pain_type", "prognosis", "literacy", "job_status"
    ]
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    
    for _ in range(NUM_RECORDS):
        full_name = fake.name()
        first_name, last_name = full_name.split(" ", 1)
        age = random.randint(49, 90)
        location = random.choice(LOCATIONS)
        illness = random.choice(ILLNESSES)
        mental_state = random.choice(MENTAL_STATES)
        pain_type = "severe mental pain" if illness == "depression" else random.choice(PAIN_TYPES)
        prognosis = "N/A" if illness == "depression" else random.choice(PROGNOSES)
        literacy = random.choice(LITERACY)
        job_status = random.choice(JOB_STATUS)


        patient_data = {
            "first name": first_name,
            "last name": last_name,
            "age": age,
            "location": location,
            "illness": illness,
            "mental_state": mental_state,
            "pain_type": pain_type,
            "prognosis": prognosis,
            "literacy": literacy,
            "job_status": job_status
        }
        csv_writer.writerow(patient_data)

        # Log the generated values to the console
        print(f"Generated patient record:")
        print(f"  First Name: {first_name}")
        print(f"  Last Name: {last_name}")
        print(f"  Age: {age}")
        print(f"  Location: {location}")
        print(f"  Illness: {illness}")
        print(f"  Mental State: {mental_state}")
        print(f"  Pain Type: {pain_type}")
        print(f"  Prognosis: {prognosis}")
        print(f"  literacy: {literacy}")
        print(f"  job_status: {job_status}")
        print("------------------------")

print(
    f"Generated {NUM_RECORDS} random patient records and saved them to {CSV_FILE_PATH}"
)
#Cancer weights 
# https://seer.cancer.gov/statfacts/html/common.html#:~:text=Breast%2C%20lung%20and%20bronchus%2C%20prostate,nearly%2050%25%20of%20all%20deaths.
