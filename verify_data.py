from rec_engine import DataBundle

b = DataBundle.load()
print("=== DATA LOADING VERIFICATION ===\n")
print(f"Pilot user data: {b.pilot_user.shape if b.pilot_user is not None else 'NOT LOADED'}")
print(f"Lab results: {b.labs.shape if b.labs is not None else 'NOT LOADED'}")
print(f"Wearable data: {b.wearable.shape if b.wearable is not None else 'NOT LOADED'}")
print(f"Microbiome: {b.microbiome.shape if b.microbiome is not None else 'NOT LOADED'}")
print(f"Metabolomics: {b.metabolomics.shape if b.metabolomics is not None else 'NOT LOADED'}")
print(f"Genomics: {b.genomics.shape if b.genomics is not None else 'NOT LOADED'}")
print(f"Medications: {b.meds.shape if b.meds is not None else 'NOT LOADED'}")
print(f"Surveys: {b.surveys.shape if b.surveys is not None else 'NOT LOADED'}")
print(f"Main peptide catalog: {b.main.shape if b.main is not None else 'NOT LOADED'}")
print(f"\nUser key detected: {b.user_key}")
