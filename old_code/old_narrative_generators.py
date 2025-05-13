# import csv
# import os
# import anthropic
# import random
# import json
# from typing import Dict, Any
# import sys

# from api_key import anthropic_key

# # Initialize the Anthropic client with the API key 
# client = anthropic.Client(api_key=anthropic_key)

# # Copy paste patient data csv title into the variable patient_csv
# patient_csv = "stratified_patient_data_20250212_200631"
# # patient_csv is used to determine file path
# CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# # Output CSV file path
# OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

# def print_with_border(text: str, width: int = 80) -> None:
#     """Print text with a decorative border."""
#     print("\n" + "="*width)
#     print(text)
#     print("="*width + "\n")

# def generate_patient_name(patient_data: Dict[str, Any], max_retries: int = 3) -> Dict[str, str]:
#     """Generate a culturally appropriate name based on patient demographics."""
#     print_with_border(f"Generating name for patient with race: {patient_data['race']}, age_group: {patient_data['age_group']}")

#     for attempt in range(max_retries):
#         try:
#             message = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=50,
#                 temperature=0.7,
#                 system="""
#                 You are an AI assistant helping generate culturally appropriate names for a 
#                 medical study. Before generating a new name, you need to look through a 
#                 list of names that have already been generated, and you must make sure 
#                 that you generate a name that is distinct from those names that have been 
#                 generated. then, Generate a full name (first and last) that would be typical 
#                 for someone of the specified race, age, and gender. Return the result as a 
#                 JSON object with 'first_name' and 'last_name' fields. Only return the JSON,
#                 no other text.
#                 """,
#                 messages=[{
#                     "role": "user",
#                     "content": [{
#                         "type": "text",
#                         "text": f"""Please generate a name given the following information:
#                         Race: {patient_data['race']}
#                         Age Group: {patient_data['age_group']}"""
#                     }]
#                 }])
            
#             print("Generated name: ", end="", flush=True)
#             response_text = message.content[0].text
#             print(response_text)
            
#             return json.loads(response_text)
#         except Exception as e:
#             print(f"Name generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
#             continue
            
#     raise ValueError("Failed to generate a valid name after multiple attempts.")

# def generate_patient_narrative(patient_data: Dict[str, Any], max_retries: int = 3) -> str:
#     """Generate a narrative for the patient using their information."""
#     print_with_border(f"Generating narrative for {patient_data['first_name']} {patient_data['last_name']}")
    
#     for attempt in range(max_retries):
#         try:
#             temperature = round(random.uniform(0.1, 1.0), 1)
#             print(f"Using temperature: {temperature}")

#             message = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=500,
#                 temperature=temperature,
#                 stream=True,
#                 system="""
#                 You are an AI assistant helping with a psychological study that analyzes 
#                 the moral convictions of medical professionals confronted with the 
#                 possibility of administering assisted dying to patients. The study involves 
#                 presenting participants with patient narratives seeking assisted dying. 
#                 Your task is to generate a short, realistic narrative for each patient 
#                 based on their information, which includes their name, age, gender, race,
#                 and mortality rate. The narrative should be written in the first person from the 
#                 patient's perspective, explaining their situation and their desire to pursue 
#                 assisted dying. It is important to note that every patient has approval from 
#                 their family to pursue assisted dying - this fact should be reflected in 
#                 the narrative. Ensure that the narrative accurately reflects the patient's 
#                 information and maintains a serious and compassionate tone appropriate for 
#                 the sensitive topic of assisted dying.

#                 The output content should be in JSON format with separate fields for:
#                 - gender (string)
#                 - narrative (string)
#                 - temperature (float)
                
#                 Make sure to provide the complete JSON string without truncation.
#                 """,
#                 messages=[{
#                     "role": "user",
#                     "content": [{
#                         "type": "text",
#                         "text": f"""Please generate a patient narrative for assisted dying based on the following information:
#                         First Name: {patient_data['first_name']}
#                         Last Name: {patient_data['last_name']}
#                         Age_group: {patient_data['age_group']}
#                         Race: {patient_data['race']}
#                         Mortality: {patient_data['mortality']}"""
#                     }]
#                 }])
            
#             print("\nGenerating narrative: ")
#             response_text = ""
#             for chunk in message:
#                 if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
#                     sys.stdout.write(chunk.delta.text)
#                     sys.stdout.flush()
#                     response_text += chunk.delta.text
#             print("\n")
            
#             json_data = json.loads(response_text)
#             json_data["temperature"] = temperature
#             return json.dumps(json_data)
#         except Exception as e:
#             print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
#             continue
            
#     raise ValueError("Failed to generate a valid JSON response after multiple attempts.")

# def main():
#     # Read patient data from the input CSV file
#     with open(CSV_FILE_PATH, "r") as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         patient_data_list = list(csv_reader)

#     print_with_border(f"Processing {len(patient_data_list)} patients")

#     # Process each patient
#     processed_patients = []
#     for i, patient_data in enumerate(patient_data_list, 1):
#         try:
#             print_with_border(f"Processing patient {i} of {len(patient_data_list)}")
            
#             # First generate a name
#             name_data = generate_patient_name(patient_data)
#             patient_data['first_name'] = name_data['first_name']
#             patient_data['last_name'] = name_data['last_name']
            
#             # Then generate the narrative
#             narrative_json = generate_patient_narrative(patient_data)
#             narrative_data = json.loads(narrative_json)
            
#             # Combine all data
#             processed_patient = {
#                 "first_name": patient_data["first_name"],
#                 "last_name": patient_data["last_name"],
#                 "age_group": patient_data["age_group"],
#                 "gender": narrative_data["gender"],
#                 "race": patient_data["race"],
#                 "mortality": patient_data["mortality"],
#                 "narrative": narrative_data["narrative"],
#                 "temperature": narrative_data["temperature"]
#             }
#             processed_patients.append(processed_patient)
            
#             print(f"\nSuccessfully processed patient: {patient_data['first_name']} {patient_data['last_name']}")
            
#         except Exception as e:
#             print(f"Error processing patient data: {str(e)}")
#             continue

#     # Write all processed data to the output CSV file
#     with open(OUTPUT_CSV_FILE_PATH, "w", newline="") as csv_file:
#         fieldnames = [
#             "first_name", "last_name", "age_group", "gender", "race", 
#             "mortality", "narrative", "temperature"
#         ]
#         csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         csv_writer.writeheader()
        
#         for patient in processed_patients:
#             csv_writer.writerow(patient)

#     print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")

# if __name__ == "__main__":
#     main()

# import csv
# import os
# import anthropic
# import random
# import json
# from typing import Dict, Any, Set
# import sys

# from api_key import anthropic_key

# # Initialize the Anthropic client with the API key 
# client = anthropic.Client(api_key=anthropic_key)

# # Copy paste patient data csv title into the variable patient_csv
# patient_csv = "stratified_patient_data_20250210_104305"
# # patient_csv is used to determine file path
# CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# # Output CSV file path
# OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

# def print_with_border(text: str, width: int = 80) -> None:
#     """Print text with a decorative border."""
#     print("\n" + "="*width)
#     print(text)
#     print("="*width + "\n")

# def generate_patient_name(patient_data: Dict[str, Any], existing_names: Set[str], max_retries: int = 3) -> Dict[str, str]:
#     """Generate a unique, culturally appropriate name based on patient demographics."""
#     print_with_border(f"Generating name for patient with race: {patient_data['race']}, age_group: {patient_data['age_group']}")
    
#     for attempt in range(max_retries):
#         try:
#             message = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=50,
#                 temperature=0.7,
#                 system=f"""
#                 You are an AI assistant helping generate culturally appropriate names for a 
#                 medical study. Generate a full name (first and last) that would be typical 
#                 for someone of the specified race, age, and gender. The name must NOT be one
#                 of these existing names: {', '.join(existing_names)}. Return the result as a 
#                 JSON object with 'first_name' and 'last_name' fields. Only return the JSON,
#                 no other text.
#                 """,
#                 messages=[{
#                     "role": "user",
#                     "content": [{
#                         "type": "text",
#                         "text": f"""Please generate a unique name given the following information:
#                         Race: {patient_data['race']}
#                         Age Group: {patient_data['age_group']}"""
#                     }]
#                 }])
            
#             print("Generated name: ", end="", flush=True)
#             response_text = message.content[0].text
#             print(response_text)
            
#             name_data = json.loads(response_text)
#             full_name = f"{name_data['first_name']} {name_data['last_name']}"
            
#             # Check if the generated name is unique
#             if full_name not in existing_names:
#                 existing_names.add(full_name)
#                 return name_data
#             else:
#                 print(f"Generated name '{full_name}' already exists. Retrying...")
#                 continue
            
#         except Exception as e:
#             print(f"Name generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
#             continue
            
#     raise ValueError("Failed to generate a unique name after multiple attempts.")

# def main():
#     # Read patient data from the input CSV file
#     with open(CSV_FILE_PATH, "r") as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         patient_data_list = list(csv_reader)

#     print_with_border(f"Processing {len(patient_data_list)} patients")

#     # Initialize set to track existing names
#     existing_names = set()
    
#     # Process each patient
#     processed_patients = []
#     for i, patient_data in enumerate(patient_data_list, 1):
#         try:
#             print_with_border(f"Processing patient {i} of {len(patient_data_list)}")
            
#             # Generate a unique name
#             name_data = generate_patient_name(patient_data, existing_names)
#             patient_data['first_name'] = name_data['first_name']
#             patient_data['last_name'] = name_data['last_name']
            
#             # Generate the narrative
#             narrative_json = generate_patient_narrative(patient_data)
#             narrative_data = json.loads(narrative_json)
            
#             # Combine all data
#             processed_patient = {
#                 "first_name": patient_data["first_name"],
#                 "last_name": patient_data["last_name"],
#                 "age_group": patient_data["age_group"],
#                 "gender": narrative_data["gender"],
#                 "race": patient_data["race"],
#                 "mortality": patient_data["mortality"],
#                 "narrative": narrative_data["narrative"],
#                 "temperature": narrative_data["temperature"]
#             }
#             processed_patients.append(processed_patient)
            
#             print(f"\nSuccessfully processed patient: {patient_data['first_name']} {patient_data['last_name']}")
            
#         except Exception as e:
#             print(f"Error processing patient data: {str(e)}")
#             continue

#     # Write all processed data to the output CSV file
#     with open(OUTPUT_CSV_FILE_PATH, "w", newline="") as csv_file:
#         fieldnames = [
#             "first_name", "last_name", "age_group", "gender", "race", 
#             "mortality", "narrative", "temperature"
#         ]
#         csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         csv_writer.writeheader()
        
#         for patient in processed_patients:
#             csv_writer.writerow(patient)

#     print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")

# if __name__ == "__main__":
#     main()

# import csv
# import os
# import anthropic
# import random
# import json
# from typing import Dict, Any, Set
# import sys

# from api_key import anthropic_key

# # Initialize the Anthropic client with the API key 
# client = anthropic.Client(api_key=anthropic_key)

# # Copy paste patient data csv title into the variable patient_csv
# patient_csv = "stratified_patient_data_20250210_104305"
# # patient_csv is used to determine file path
# CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# # Output CSV file path
# OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

# def print_with_border(text: str, width: int = 80) -> None:
#     """Print text with a decorative border."""
#     print("\n" + "="*width)
#     print(text)
#     print("="*width + "\n")

# def generate_patient_name(patient_data: Dict[str, Any], existing_names: Set[str], max_retries: int = 3) -> Dict[str, str]:
#     """Generate a unique, culturally appropriate name based on patient demographics."""
#     print_with_border(f"Generating name for patient with race: {patient_data['race']}, age_group: {patient_data['age_group']}")
    
#     for attempt in range(max_retries):
#         try:
#             message = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=50,
#                 temperature=0.7,
#                 system=f"""
#                 You are an AI assistant helping generate culturally appropriate names for a 
#                 medical study. Generate a full name (first and last) that would be typical 
#                 for someone of the specified race, age, and gender. The name must NOT be one
#                 of these existing names: {', '.join(existing_names)}. Return the result as a 
#                 JSON object with 'first_name' and 'last_name' fields. Only return the JSON,
#                 no other text.
#                 """,
#                 messages=[{
#                     "role": "user",
#                     "content": [{
#                         "type": "text",
#                         "text": f"""Please generate a unique name given the following information:
#                         Race: {patient_data['race']}
#                         Age Group: {patient_data['age_group']}"""
#                     }]
#                 }])
            
#             print("Generated name: ", end="", flush=True)
#             response_text = message.content[0].text
#             print(response_text)
            
#             name_data = json.loads(response_text)
#             full_name = f"{name_data['first_name']} {name_data['last_name']}"
            
#             # Check if the generated name is unique
#             if full_name not in existing_names:
#                 existing_names.add(full_name)
#                 return name_data
#             else:
#                 print(f"Generated name '{full_name}' already exists. Retrying...")
#                 continue
            
#         except Exception as e:
#             print(f"Name generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
#             continue
            
#     raise ValueError("Failed to generate a unique name after multiple attempts.")

# def generate_patient_narrative(patient_data: Dict[str, Any], max_retries: int = 3) -> str:
#     """Generate a narrative for the patient using their information."""
#     print_with_border(f"Generating narrative for {patient_data['first_name']} {patient_data['last_name']}")
    
#     for attempt in range(max_retries):
#         try:
#             temperature = round(random.uniform(0.1, 1.0), 1)
#             print(f"Using temperature: {temperature}")

#             message = client.messages.create(
#                 model="claude-3-5-sonnet-20241022",
#                 max_tokens=500,
#                 temperature=temperature,
#                 stream=True,
#                 system="""
#                 You are an AI assistant helping with a psychological study that analyzes 
#                 the moral convictions of medical professionals confronted with the 
#                 possibility of administering assisted dying to patients. The study involves 
#                 presenting participants with patient narratives seeking assisted dying. 
#                 Your task is to generate a short, realistic narrative for each patient 
#                 based on their information, which includes their name, age, gender, race,
#                 and mortality rate. The narrative should be written in the first person from the 
#                 patient's perspective, explaining their situation and their desire to pursue 
#                 assisted dying. It is important to note that every patient has approval from 
#                 their family to pursue assisted dying - this fact should be reflected in 
#                 the narrative. Ensure that the narrative accurately reflects the patient's 
#                 information and maintains a serious and compassionate tone appropriate for 
#                 the sensitive topic of assisted dying.

#                 IMPORTANT: You cannot mention any of the following
#                 - The patient's occupation
#                 - What kind of illness you have
#                 - How the cancer affects the patient 
#                 - Do not mention personal interests or hobbies
                

#                 The output content should be in JSON format with separate fields for:
#                 - gender (string)
#                 - narrative (string)
#                 - temperature (float)
                
#                 Make sure to provide the complete JSON string without truncation.
#                 """,
#                 messages=[{
#                     "role": "user",
#                     "content": [{
#                         "type": "text",
#                         "text": f"""Please generate a patient narrative for assisted dying based on the following information:
#                         First Name: {patient_data['first_name']}
#                         Last Name: {patient_data['last_name']}
#                         Age_group: {patient_data['age_group']}
#                         Race: {patient_data['race']}
#                         Mortality: {patient_data['mortality']}"""
#                     }]
#                 }])
            
#             print("\nGenerating narrative: ")
#             response_text = ""
#             for chunk in message:
#                 if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
#                     sys.stdout.write(chunk.delta.text)
#                     sys.stdout.flush()
#                     response_text += chunk.delta.text
#             print("\n")
            
#             json_data = json.loads(response_text)
#             json_data["temperature"] = temperature
#             return json.dumps(json_data)
#         except Exception as e:
#             print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
#             continue
            
#     raise ValueError("Failed to generate a valid JSON response after multiple attempts.")

# def main():
#     # Read patient data from the input CSV file
#     with open(CSV_FILE_PATH, "r") as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         patient_data_list = list(csv_reader)

#     print_with_border(f"Processing {len(patient_data_list)} patients")

#     # Initialize set to track existing names
#     existing_names = set()
    
#     # Process each patient
#     processed_patients = []
#     for i, patient_data in enumerate(patient_data_list, 1):
#         try:
#             print_with_border(f"Processing patient {i} of {len(patient_data_list)}")
            
#             # Generate a unique name
#             name_data = generate_patient_name(patient_data, existing_names)
#             patient_data['first_name'] = name_data['first_name']
#             patient_data['last_name'] = name_data['last_name']
            
#             # Generate the narrative
#             narrative_json = generate_patient_narrative(patient_data)
#             narrative_data = json.loads(narrative_json)
            
#             # Combine all data
#             processed_patient = {
#                 "first_name": patient_data["first_name"],
#                 "last_name": patient_data["last_name"],
#                 "age_group": patient_data["age_group"],
#                 "gender": narrative_data["gender"],
#                 "race": patient_data["race"],
#                 "mortality": patient_data["mortality"],
#                 "narrative": narrative_data["narrative"],
#                 "temperature": narrative_data["temperature"]
#             }
#             processed_patients.append(processed_patient)
            
#             print(f"\nSuccessfully processed patient: {patient_data['first_name']} {patient_data['last_name']}")
            
#         except Exception as e:
#             print(f"Error processing patient data: {str(e)}")
#             continue

#     # Write all processed data to the output CSV file
#     with open(OUTPUT_CSV_FILE_PATH, "w", newline="") as csv_file:
#         fieldnames = [
#             "first_name", "last_name", "age_group", "gender", "race", 
#             "mortality", "narrative", "temperature"
#         ]
#         csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         csv_writer.writeheader()
        
#         for patient in processed_patients:
#             csv_writer.writerow(patient)

#     print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")

# if __name__ == "__main__":
#     main()