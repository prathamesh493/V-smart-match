import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURATION ---
# IMPORTANT: Replace this with the actual path to your Firebase service account key JSON file.
# You can download this from your Firebase project settings: Project Settings > Service accounts > Generate new private key.
SERVICE_ACCOUNT_KEY_PATH = "/home/gm/Desktop/vsmart-backend/firebase-credentials.json"

# --- INITIALIZATION ---
def initialize_firestore():
    """Initializes the Firebase Admin SDK."""
    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print(f"🚨 Error: Service account key not found at '{SERVICE_ACCOUNT_KEY_PATH}'")
        print("Please update the SERVICE_ACCOUNT_KEY_PATH variable with the correct path.")
        exit()
        
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"🚨 Error initializing Firebase: {e}")
        exit()

# --- MAIN LOGIC ---
def backfill_match_data():
    """
    Iterates through all 'matches' documents, fetches the corresponding 
    job description, and updates the match with 'recruiterId' and 'jobTitle'.
    """
    db = initialize_firestore()
    
    matches_ref = db.collection("matches")
    jobs_ref = db.collection("job_descriptions")
    
    # Using stream() is memory-efficient for large collections
    all_matches = matches_ref.stream()
    
    total_checked = 0
    total_updated = 0
    total_errors = 0
    
    # Firestore batches can hold up to 500 operations
    batch = db.batch()
    operations_in_batch = 0
    
    print("\n🚀 Starting backfill process...")

    for match_doc in all_matches:
        total_checked += 1
        match_data = match_doc.to_dict()
        match_id = match_doc.id

        # Skip documents that have already been updated
        if "recruiterId" in match_data:
            continue

        job_id = match_data.get("jobDescriptionId")
        if not job_id:
            print(f"⚠️  Skipping match '{match_id}': Missing 'jobDescriptionId'.")
            total_errors += 1
            continue

        try:
            # Fetch the corresponding job description
            job_doc = jobs_ref.document(job_id).get()
            
            if not job_doc.exists:
                print(f"⚠️  Skipping match '{match_id}': Corresponding job '{job_id}' not found.")
                total_errors += 1
                continue
            
            job_data = job_doc.to_dict()
            recruiter_id = job_data.get("user_id")
            job_title = job_data.get("job_title", "Untitled Job") # Default value if missing
            
            if not recruiter_id:
                print(f"⚠️  Skipping match '{match_id}': Job '{job_id}' is missing 'user_id'.")
                total_errors += 1
                continue

            # Add the update operation to the batch
            update_ref = matches_ref.document(match_id)
            batch.update(update_ref, {
                "recruiterId": recruiter_id,
                "jobTitle": job_title
            })
            operations_in_batch += 1
            total_updated += 1

            # Commit the batch when it's full to avoid memory issues and errors
            if operations_in_batch >= 499:
                print(f"Writing batch of {operations_in_batch} updates to Firestore...")
                batch.commit()
                # Start a new batch
                batch = db.batch()
                operations_in_batch = 0

        except Exception as e:
            print(f"🚨 An error occurred processing match '{match_id}': {e}")
            total_errors += 1

    # Commit any remaining operations in the last batch
    if operations_in_batch > 0:
        print(f"Writing final batch of {operations_in_batch} updates to Firestore...")
        batch.commit()
        
    print("\n---")
    print("✅ Backfill process completed!")
    print(f"📊 Summary:")
    print(f"   - Documents checked: {total_checked}")
    print(f"   - Documents updated: {total_updated}")
    print(f"   - Errors/Skips:      {total_errors}")
    print("---\n")


if __name__ == "__main__":
    backfill_match_data()