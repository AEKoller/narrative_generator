import csv
import os
import anthropic
import json
from typing import Dict, Any, List # Set is no longer used
import sys

# Assuming api_key.py is in the same directory or accessible in PYTHONPATH
from api_key import anthropic_key

# Initialize the Anthropic client with the API key
client = anthropic.Client(api_key=anthropic_key)

# Copy paste patient data csv title into the variable patient_csv
patient_csv = "stratified_patient_data_20250513_123759"
# patient_csv is used to determine file path
CSV_FILE_PATH = f"patient_data/{patient_csv}.csv"

# Output CSV file path
OUTPUT_CSV_FILE_PATH = f"patient_data/{patient_csv}_with_narratives.csv"

def print_with_border(text: str, width: int = 80) -> None:
    """Print text with a decorative border."""
    print("\n" + "="*width)
    print(text)
    print("="*width + "\n")

def generate_patient_narrative(patient_data: Dict[str, Any], existing_narratives: List[str], max_retries: int = 3):
    """Generate a unique narrative for the patient using their information."""
    # Uses .get() for safer access in case a key is unexpectedly missing
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
            temperature = 0.7  # Fixed temperature
            print(f"Using temperature: {temperature}")

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022", # Using the model name you provided
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
                - temperature (float)

                Make sure to provide the complete JSON string without truncation.
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

            json_data = json.loads(response_text)
            json_data["temperature"] = temperature
            return json.dumps(json_data)
        except Exception as e:
            print(f"Narrative generation attempt {attempt + 1} failed: {str(e)}. Retrying...")
            continue

    raise ValueError("Failed to generate a valid JSON response after multiple attempts.")

def main():
    # Read patient data from the input CSV file
    try:
        with open(CSV_FILE_PATH, "r", newline='') as csv_file: # Added newline='' for robust CSV handling
            csv_reader = csv.DictReader(csv_file)
            # Check if 'pain_intensity' is in the field names, if not, raise an error or warning
            if 'pain_intensity' not in csv_reader.fieldnames:
                print(f"ERROR: The CSV file '{CSV_FILE_PATH}' must contain a column named 'pain_intensity'.")
                print(f"Detected columns: {csv_reader.fieldnames}")
                return # Exit if the required column is missing

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
            # Adding a check for pain_intensity key for robustness, though DictReader should provide it.
            if 'pain_intensity' not in current_patient_data or not current_patient_data['pain_intensity']:
                print(f"Warning: Patient {i} is missing 'pain_intensity' data in the CSV. Skipping or handling as default if necessary.")
                # Decide how to handle: skip, use a default, or raise error. For now, it will pass None or empty.
                # The .get() in generate_patient_narrative will handle it gracefully as 'N/A' or None.

            print(f"Using data from CSV - Age Group: {current_patient_data.get('age_group')}, Race: {current_patient_data.get('race')}, Pain Intensity: {current_patient_data.get('pain_intensity')}")

            narrative_json = generate_patient_narrative(current_patient_data, existing_narratives)
            narrative_data = json.loads(narrative_json)

            existing_narratives.append(narrative_data['narrative'])

            processed_patient = {
                "age_group": current_patient_data.get("age_group"),
                "gender": narrative_data["gender"],
                "race": current_patient_data.get("race"),
                "pain_intensity": current_patient_data.get("pain_intensity"), # From CSV
                "narrative": narrative_data["narrative"],
                "temperature": narrative_data["temperature"]
            }
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
            fieldnames = [
                "age_group", "gender", "race", "pain_intensity",
                "narrative", "temperature"
            ]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(processed_patients) # Use writerows for efficiency
        print_with_border(f"Generated narratives for {len(processed_patients)} patients and saved them to {OUTPUT_CSV_FILE_PATH}")
    except IOError as e:
        print(f"ERROR: Could not write to output CSV file {OUTPUT_CSV_FILE_PATH}: {e}")


if __name__ == "__main__":
    main()