import csv
import os
import anthropic
import json
import re
from typing import Dict, Any, List
import sys

# We first import the API key from a the api_key file within the folder
# In our case, the api_key.py file contains the anthropic_key variable
# You may not have the api_key.py file. If you do not, create one, and then 
# add the following line to it:
# anthropic_key = "your_anthropic_api_key_here"
from api_key import anthropic_key

# Once we have our API key, we can initialize the Anthropic client
# We also save it to a variable for later use
client = anthropic.Client(api_key=anthropic_key)

# What we need to do next is to copy paste the patient data csv title into the variable patient_csv
# This contains the patient information that we will use to generate narratives
patient_csv = "stratified_patient_data_20250602_121539"
# We create a file path for the CSV file using the patient_csv variable
CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# We also define the output CSV file path where we will save the generated narratives
OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

def print_with_border(text: str, width: int = 80):
    """
    Print text with a decorative border within terminal.

    Args:
        text: The text to print within the border.
        width: The width of the border.
    Returns:
        The text printed with a border.
    """
    print("\n" + "="*width)
    print(text)
    print("="*width + "\n")


def extract_json_from_response(response_text: str):
    """
    Extract JSON content from a response that may contain markdown code blocks.
    Args:
        response_text: The text response from the AI, which contains JSON in code blocks.
    Returns:
        A string containing the JSON content extracted from the response.
        If no code blocks are found, returns the entire response text as JSON.
    
    """
    # We use a regex pattern to find JSON content within markdown code blocks
    # This pattern looks for ```json followed by any content until the closing ```
    json_pattern = r'```json\s*(.*?)\s*```'
    # We use re.DOTALL to allow the dot to match newlines, enabling multiline JSON extraction
    # We search for the pattern in the response text
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    # If a match is found, we return the first capturing group which contains the JSON content
    if match:
        return match.group(1)
    
    # If no code blocks found, assume the entire response is JSON
    return response_text

def generate_patient_narrative(patient_data: Dict[str, Any], existing_narratives: List[str], max_retries: int = 3):
    """
    This is the main function that generates a unique narrative for a patient
    Args:
        patient_data: A dictionary containing patient information
        existing_narratives: A list of previously generated narratives to ensure uniqueness
        max_retries: The maximum number of retries for generating a narrative in case of errors
    Returns:
        A JSON string containing the generated narrative and other patient information
    """
    # Here, we call the print_with_border function to print a message with a border
    # Uses .get() to safely access patient data fields in case a key is unexpectedly missing
    # This prevents KeyError if a key is not present in the patient_data dictionary
    # This allows us to see the patient information in terminal as we generate the narrative
    print_with_border(
        f"Generating narrative for patient (Age Group: {patient_data.get('age_group', 'N/A')}, "
        f"Race: {patient_data.get('race', 'N/A')}, "
        f"Pain Intensity: {patient_data.get('pain_intensity', 'N/A')})"
    )

    
    narrative_examples = ""
    if existing_narratives:
        narrative_examples = "\n\nPreviously generated narratives:\n" + "\n---\n".join(
            [f"Narrative {i+1}:\n{narrative}" for i, narrative in enumerate(existing_narratives[-3:])]
        )

    for attempt in range(max_retries):
        try:
            temperature = .7  # Changed from 0.0 to 0.25
            print(f"Using temperature: {temperature}")

            message = client.messages.create(
                model="claude-4-sonnet-20250514", 
                max_tokens=500,
                temperature=temperature,
                stream=True,
                system=f"""
                You are an AI assistant helping with a psychological study that analyzes
                the moral convictions of medical professionals confronted with the
                possibility of administering assisted dying to patients. The study involves
                presenting participants with patient narratives seeking assisted dying.
                Your task is to generate a short, realistic narrative for each patient
                based on their information, which includes their age, gender, race, and pain intensity.

                The narrative should be:
                1. Written in the first person from the patient's perspective
                2. Explain their situation and desire to pursue assisted dying
                3. Mention that they have family approval
                4. Be DISTINCTLY DIFFERENT from previous narratives in terms of:
                   - Narrative structure
                   - Word choice and phrasing
                   - Emotional tone and perspective
                   - Reasoning and decision-making process

                IMPORTANT RESTRICTIONS:
                - Do not mention the patient's occupation
                - Do not specify the type of illness
                - Do not describe how the illness affects the patient
                - Do not mention personal interests or hobbies
                - Do not mention personal or cultural beliefs

                {narrative_examples}

                The output content should be in JSON format with separate fields for:
                - gender (string)
                - narrative (string)

                Provide the JSON response without any markdown formatting or code blocks.
                """,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f"""Please generate a unique patient narrative for assisted dying based on the following information:
                        Age Group: {patient_data.get('age_group')}
                        Race: {patient_data.get('race')}
                        Pain Intensity: {patient_data.get('pain_intensity')}"""
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

            # Extract JSON from the response (handles markdown code blocks)
            json_content = extract_json_from_response(response_text)
            json_data = json.loads(json_content)
            
            # Store both the AI-generated temperature (if any) and actual temperature
            ai_generated_temp = json_data.get("temperature", None)
            if ai_generated_temp is not None:
                print(f"AI suggested temperature: {ai_generated_temp}")
                json_data["ai_suggested_temperature"] = ai_generated_temp
            
            # Always use our actual temperature value for the output
            json_data["temperature"] = temperature
            return json.dumps(json_data)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in attempt {attempt + 1}: {str(e)}")
            print(f"Response text: {response_text[:200]}...")  # Show first 200 chars for debugging
            continue
        except Exception as e:
            print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
            continue

    raise ValueError("Failed to generate a valid JSON response after multiple attempts.")

def main():
    # Read patient data from the input CSV file
    try:
        with open(CSV_FILE_PATH, "r", newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # Check if 'pain_intensity' is in the field names, if not, raise an error or warning
            if 'pain_intensity' not in csv_reader.fieldnames:
                print(f"ERROR: The CSV file '{CSV_FILE_PATH}' must contain a column named 'pain_intensity'.")
                print(f"Detected columns: {csv_reader.fieldnames}")
                return

            patient_data_list = list(csv_reader)
    except FileNotFoundError:
        print(f"ERROR: Input CSV file not found at {CSV_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR: Could not read CSV file: {e}")
        return

    print_with_border(f"Processing {len(patient_data_list)} patients from {CSV_FILE_PATH}")

    existing_narratives = []
    processed_patients = []

    for i, patient_data_row in enumerate(patient_data_list, 1):
        current_patient_data = dict(patient_data_row)
        try:
            print_with_border(f"Processing patient {i} of {len(patient_data_list)}")

            # Ensure necessary keys are present from the CSV
            if 'pain_intensity' not in current_patient_data or not current_patient_data['pain_intensity']:
                print(f"Warning: Patient {i} is missing 'pain_intensity' data in the CSV. Skipping or handling as default if necessary.")

            print(f"Using data from CSV - Age Group: {current_patient_data.get('age_group')}, Race: {current_patient_data.get('race')}, Pain Intensity: {current_patient_data.get('pain_intensity')}")

            narrative_json = generate_patient_narrative(current_patient_data, existing_narratives)
            narrative_data = json.loads(narrative_json)

            existing_narratives.append(narrative_data['narrative'])

            processed_patient = {
                "age_group": current_patient_data.get("age_group"),
                "gender": narrative_data["gender"],
                "race": current_patient_data.get("race"),
                "pain_intensity": current_patient_data.get("pain_intensity"),
                "narrative": narrative_data["narrative"],
                "temperature": narrative_data["temperature"]
            }
            
            # Add AI suggested temperature if it exists
            if "ai_suggested_temperature" in narrative_data:
                processed_patient["ai_suggested_temperature"] = narrative_data["ai_suggested_temperature"]
            
            processed_patients.append(processed_patient)

            print(f"\nSuccessfully processed patient {i} (Age Group: {current_patient_data.get('age_group')}, Pain: {current_patient_data.get('pain_intensity')})")

        except Exception as e:
            print(f"Error processing patient data for row {i} (Data: {current_patient_data}): {str(e)}")
            continue

    if not processed_patients:
        print("No patients were processed. Output file will not be created.")
        return

    # Write all processed data to the output CSV file
    try:
        with open(OUTPUT_CSV_FILE_PATH, "w", newline="") as csv_file:
            # Determine fieldnames based on whether we have AI suggested temperatures
            fieldnames = [
                "age_group", "gender", "race", "pain_intensity",
                "narrative", "temperature"
            ]
            
            # Check if any patient has ai_suggested_temperature
            if any("ai_suggested_temperature" in p for p in processed_patients):
                fieldnames.append("ai_suggested_temperature")
            
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(processed_patients)
        print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")
    except IOError as e:
        print(f"ERROR: Could not write to output CSV file {OUTPUT_CSV_FILE_PATH}: {e}")

if __name__ == "__main__":
    main()