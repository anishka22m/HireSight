import pandas as pd
import os

def create_skill_lookup(file_path):
    """
    Loads ESCO individual skills for validation using UTF-8 encoding.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Ensure 'skills_en.csv' is in the data folder.")
        return None

    try:
        # Explicitly setting encoding to utf-8 for ESCO data
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Check for standard ESCO column names
        if 'preferredLabel' in df.columns:
            skill_col = 'preferredLabel'
        elif 'label' in df.columns:
            skill_col = 'label'
        else:
            print(f"Columns found: {df.columns.tolist()}")
            return None

        # Clean and convert to a lowercase set
        esco_skills = set(df[skill_col].str.lower().str.strip())
        
        # Using plain text instead of emojis to avoid UnicodeEncodeError
        print(f"SUCCESS: Loaded {len(esco_skills)} individual skills from ESCO.")
        return esco_skills

    except Exception as e:
        print(f"FAILED to read CSV: {e}")
        return None

if __name__ == "__main__":
    # Ensure this path points to the 9,084 KB 'skills_en.csv' file
    PATH = "backend\\data\\skills_en.csv" 
    skills_set = create_skill_lookup(PATH)
    
    # Test specific terms to verify the "Gold List" logic
    test_words = ["python", "javascript", "machine learning", "recruitment", "brands"]
    
    print("\n--- TEST VALIDATION ---")
    if skills_set:
        for word in test_words:
            is_valid = word in skills_set
            status = "VALID SKILL" if is_valid else "NOT IN ESCO"
            print(f"'{word}' -> {status}")