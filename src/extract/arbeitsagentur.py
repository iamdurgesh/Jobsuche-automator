import requests
import pandas as pd

API_BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
CLIENT_ID = "jobboerse-jobsuche"

def fetch_jobs(job_title, location="", limit=50, page=1):
    headers = {
        "X-API-Key": CLIENT_ID,
        "User-Agent": "job-search-script"
    }
    
    params = {
        "beruf": job_title,
        "arbeitsort": location,
        "page": page,
        "size": limit
    }
    
    response = requests.get(API_BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error (Status {response.status_code}): {response.text}")
        return None

def extract_job_details(raw_jobs):
    job_list = []
    
    if not raw_jobs or "stellenangebote" not in raw_jobs:
        print("⚠️ No job listings found.")
        return pd.DataFrame()
    
    for job in raw_jobs["stellenangebote"]:
        arbeitsort = job.get("arbeitsort", {})
        koordinaten = arbeitsort.get("koordinaten", {})
        
        job_data = {
            "Job Title": job.get("beruf", "N/A"),
            "Company": job.get("arbeitgeber", "N/A"),
            "Location": arbeitsort.get("ort", "N/A"),
            "Postal Code": arbeitsort.get("plz", "N/A"),
            "Street": arbeitsort.get("strasse", "N/A"),
            "Region": arbeitsort.get("region", "N/A"),
            "Country": arbeitsort.get("land", "N/A"),
            "Latitude": koordinaten.get("lat", "N/A"),
            "Longitude": koordinaten.get("lon", "N/A"),
            "Job Reference Number": job.get("refnr", "N/A"),
            "Modification Timestamp": job.get("modifikationsTimestamp", "N/A"),
            "Job URL": f"https://jobboerse.arbeitsagentur.de/vamJB/{job.get('hashId', '')}"
        }
        job_list.append(job_data)
    
    jobs_df = pd.DataFrame(job_list)
    return jobs_df

def get_latest_jobs(job_title, location="", limit=50):
    raw_data = fetch_jobs(job_title, location, limit)
    jobs_df = extract_job_details(raw_data)

    if jobs_df.empty:
        print("❌ No matching jobs found.")
    else:
        # Convert to datetime and sort by latest
        jobs_df['Modification Timestamp'] = pd.to_datetime(
            jobs_df['Modification Timestamp'], errors='coerce'
        )
        jobs_df.sort_values(by='Modification Timestamp', ascending=False, inplace=True)
        print(jobs_df.head(10).to_string(index=False))  # Display top 10 latest jobs

    return jobs_df

def display_jobs_table(jobs_df, num_rows=10):
    if jobs_df.empty:
        print("❌ No job listings available to display.")
        return
    
    display_columns = [
        "Job Title",
        "Company",
        "Location",
        "Region",
        "Country",
        "Modification Timestamp",
        "Job URL"
    ]
    
    # Select only the columns we want to display
    display_df = jobs_df[display_columns].head(num_rows)
    
    # Adjust the DataFrame display settings
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print("\n📌 Latest Job Listings:")
    print(display_df.to_string(index=False))

if __name__ == "__main__":
    job_title = input("Enter job title: ")
    location = input("Enter location (optional): ")
    job_data = get_latest_jobs(job_title, location, limit=50)

    if not job_data.empty:
        job_data.to_csv("latest_job_listings.csv", index=False)
        print("✅ Latest job listings saved to latest_job_listings.csv")
        display_jobs_table(job_data) 
