import csv
import os
import anthropic
import random
import json
from typing import Dict, Any, Set, List
import sys

from api_key import anthropic_key

# Initialize the Anthropic client with the API key 
client = anthropic.Client(api_key=anthropic_key)

# Copy paste patient data csv title into the variable patient_csv
patient_csv = "stratified_patient_data_20250213_150823"
# patient_csv is used to determine file path
CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# Output CSV file path
OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

def print_with_border(text: str, width: int = 80) -> None:
    """Print text with a decorative border."""
    print("\n" + "="*width)
    print(text)
    print("="*width + "\n")

def generate_patient_name(patient_data: Dict[str, Any], existing_names: Set[str], max_retries: int = 3) -> Dict[str, str]:
    """Generate a unique, culturally appropriate name based on patient demographics."""
    print_with_border(f"Generating name for patient with race: {patient_data['race']}, age_group: {patient_data['age_group']}")
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=50,
                temperature=0.7,
                system=f"""
                You are an AI assistant helping generate culturally appropriate names for a 
                medical study. Generate a full name (first and last) that would be typical 
                for someone of the specified race, age, and gender. The name must NOT be one
                of these existing names: {', '.join(existing_names)}. Return the result as a 
                JSON object with 'first_name' and 'last_name' fields. Only return the JSON,
                no other text.
                """,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"""Please generate a unique name given the following information:
                        Race: {patient_data['race']}
                        Age Group: {patient_data['age_group']}"""
                    }]
                }])
            
            print("Generated name: ", end="", flush=True)
            response_text = message.content[0].text
            print(response_text)
            
            name_data = json.loads(response_text)
            full_name = f"{name_data['first_name']} {name_data['last_name']}"
            
            # Check if the generated name is unique
            if full_name not in existing_names:
                existing_names.add(full_name)
                return name_data
            else:
                print(f"Generated name '{full_name}' already exists. Retrying...")
                continue
            
        except Exception as e:
            print(f"Name generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
            continue
            
    raise ValueError("Failed to generate a unique name after multiple attempts.")

def generate_patient_narrative(patient_data: Dict[str, Any], existing_narratives: List[str], max_retries: int = 3) -> str:
    """Generate a unique narrative for the patient using their information."""
    print_with_border(f"Generating narrative for {patient_data['first_name']} {patient_data['last_name']}")
    
    # Format existing narratives for the prompt
    narrative_examples = ""
    if existing_narratives:
        narrative_examples = "\n\nPreviously generated narratives:\n" + "\n---\n".join(
            [f"Narrative {i+1}:\n{narrative}" for i, narrative in enumerate(existing_narratives[-10:])]  # Show last 3 narratives
        )
    
    for attempt in range(max_retries):
        try:
            # temperature = round(random.uniform(0.1, 1.0), 1)
            temperature = .8
            print(f"Using temperature: {temperature}")

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=temperature,
                stream=True,
                system=f"""
                You are an AI assistant helping with a psychological study that analyzes 
                the moral convictions of medical professionals confronted with the 
                possibility of administering assisted dying to patients. The study involves 
                presenting participants with patient narratives seeking assisted dying. 
                Your task is to generate a short, realistic narrative for each patient 
                based on their information, which includes their name, age, gender, race,
                and mortality rate. 

                The narrative should be:
                1. Written in the first person from the patient's perspective. 
                2. Explain their situation and desire to pursue assisted dying
                3. Mention that they have family approval
                4. Be DISTINCTLY DIFFERENT from previous narratives in terms of:
                   - Narrative structure
                   - Word choice and phrasing
                   - Emotional tone and perspective
                   - Reasoning and decision-making process
                5. Mention the patient's name

                IMPORTANT RESTRICTIONS:
                - Do not mention the patient's occupation
                - Do not specify the type of illness
                - Do not describe how the illness affects the patient
                - Do not mention personal interests or hobbies
                - Do not mention personal or cultural beliefs
                - Do not create an age for the patient. The patient may only 
                  allude to their age.

                {narrative_examples}

                The output content should be in JSON format with separate fields for:
                - gender (string)
                - narrative (string)
                - temperature (float)
                
                Make sure to provide the complete JSON string without truncation.
                """,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"""Please generate a unique patient narrative for assisted dying based on the following information:
                        First Name: {patient_data['first_name']}
                        Last Name: {patient_data['last_name']}
                        Age_group: {patient_data['age_group']}
                        Race: {patient_data['race']}
                        Mortality: {patient_data['mortality']}"""
                    }]
                }])
            
            print("\nGenerating narrative: ")
            response_text = ""
            for chunk in message:
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    sys.stdout.write(chunk.delta.text)
                    sys.stdout.flush()
                    response_text += chunk.delta.text
            print("\n")
            
            json_data = json.loads(response_text)
            json_data["temperature"] = temperature
            return json.dumps(json_data)
        except Exception as e:
            print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
            continue
            
    raise ValueError("Failed to generate a valid JSON response after multiple attempts.")


def patient_narrative_editor(narrative_data, patient_data: Dict[str, Any], existing_narratives: List[str], max_retries: int = 3) -> str:
    """Generate a unique narrative for the patient using their information."""
    print_with_border(f"Editing narrative for {patient_data['first_name']} {patient_data['last_name']}")
    
    # Format existing narratives for the prompt
    narrative_examples = ""
    if existing_narratives:
        narrative_examples = "\n\nPreviously generated narratives:\n" + "\n---\n".join(
            [f"Narrative {i+1}:\n{narrative}" for i, narrative in enumerate(existing_narratives[-32:])] 
        )
    
    for attempt in range(max_retries):
        try:
            # temperature = round(random.uniform(0.1, 1.0), 1)
            temperature = .8
            print(f"Using temperature: {temperature}")

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=temperature,
                stream=True,
                system=f"""
                You are an AI assistant helping with a psychological study that analyzes 
                the moral convictions of medical professionals confronted with the 
                possibility of administering assisted dying to patients. The study involves 
                presenting participants with patient narratives seeking assisted dying. 
                Your task is to edit a generated narrative, and make sure it is distinct
                from the previously generated narratives. In general, the narrative should 
                be a short, realistic narrative for each patient based on their information, 
                which includes their name, age, gender, race, and mortality rate. 

                The narrative should be:
                1. Written in the first person from the patient's perspective. 
                2. Explain their situation and desire to pursue assisted dying
                3. Mention that they have family approval
                4. Be DISTINCTLY DIFFERENT from previous narratives in terms of:
                   - Narrative structure
                   - Word choice and phrasing
                   - Emotional tone and perspective
                   - Reasoning and decision-making process
                5. Mention the patient's name

                IMPORTANT RESTRICTIONS - THE NARRATIVE SHOULD NOT:
                - Mention the patient's occupation
                - Specify the type of illness
                - Describe how the illness affects the patient
                - Mention personal interests or hobbies
                - Mention personal or cultural beliefs
                - Create an age for the patient. The patient may only 
                  allude to their age.

                Here is the current narrative to be edited:
                {narrative_data}

                Here are the narrative examples. Please look through each one carefully
                and make sure that the narrative you are currently editing is as 
                distinct as possible from the previously generated narratives.

                NARRATIVE EXAMPLES:
                {narrative_examples}

                The output content should be in JSON format with separate fields for:
                - gender (string)
                - narrative (string)
                - temperature (float)
                
                Make sure to provide the complete JSON string without truncation.
                """,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"""Please generate a unique patient narrative for assisted dying based on the following information:
                        First Name: {patient_data['first_name']}
                        Last Name: {patient_data['last_name']}
                        Age_group: {patient_data['age_group']}
                        Race: {patient_data['race']}
                        Mortality: {patient_data['mortality']}"""
                    }]
                }])
            
            print("\nGenerating narrative: ")
            response_text = ""
            for chunk in message:
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    sys.stdout.write(chunk.delta.text)
                    sys.stdout.flush()
                    response_text += chunk.delta.text
            print("\n")
            
            json_data = json.loads(response_text)
            json_data["temperature"] = temperature
            return json.dumps(json_data)
        except Exception as e:
            print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
            continue
            
    raise ValueError("Failed to generate a valid JSON response after multiple attempts.")


def main():
    # Read patient data from the input CSV file
    with open(CSV_FILE_PATH, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        patient_data_list = list(csv_reader)

    print_with_border(f"Processing {len(patient_data_list)} patients")

    # Initialize tracking sets/lists
    existing_names = set()
    existing_narratives = []
    
    # Process each patient
    processed_patients = []
    for i, patient_data in enumerate(patient_data_list, 1):
        try:
            print_with_border(f"Processing patient {i} of {len(patient_data_list)}")
            
            # Generate a unique name
            name_data = generate_patient_name(patient_data, existing_names)
            patient_data['first_name'] = name_data['first_name']
            patient_data['last_name'] = name_data['last_name']
            
            # Generate the narrative
            narrative_json = generate_patient_narrative(patient_data, existing_narratives)
            narrative_data = json.loads(narrative_json)

            # Edit the narrative 
            edited_json = patient_narrative_editor(narrative_data, patient_data, existing_narratives)
            edited_data = json.loads(edited_json)
            
            # Add the new narrative to our tracking list
            existing_narratives.append(edited_data['narrative'])
            
            # Combine all data
            processed_patient = {
                "first_name": patient_data["first_name"],
                "last_name": patient_data["last_name"],
                "age_group": patient_data["age_group"],
                "gender": narrative_data["gender"],
                "race": patient_data["race"],
                "mortality": patient_data["mortality"],
                "narrative": narrative_data["narrative"],
                "temperature": narrative_data["temperature"]
            }
            processed_patients.append(processed_patient)
            
            print(f"\nSuccessfully processed patient: {patient_data['first_name']} {patient_data['last_name']}")
            
        except Exception as e:
            print(f"Error processing patient data: {str(e)}")
            continue

    # Write all processed data to the output CSV file
    with open(OUTPUT_CSV_FILE_PATH, "w", newline="") as csv_file:
        fieldnames = [
            "first_name", "last_name", "age_group", "gender", "race", 
            "mortality", "narrative", "temperature"
        ]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        
        for patient in processed_patients:
            csv_writer.writerow(patient)

    print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")

if __name__ == "__main__":
    main()