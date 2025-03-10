import requests
import pandas as pd

API_KEY = 'jobboerse-jobsuche'

def get_latest_job(keyword, location="", size=1):
    headers = {
        "X-API-Key": API_KEY,
        "User-Agent": "job-detail-fetcher"
    }

    search_url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    params = {
        "beruf": keyword,
        "arbeitsort": location,
        "size": size,
        "page": 1
    }

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    jobs = response.json().get("stellenangebote", [])

    if not jobs:
        print(" No job listings found.")
        return None

    # Get the most recent job based on modification timestamp
    latest_job = max(jobs, key=lambda x: x.get('modifikationsTimestamp', ''))
    return latest_job

def get_job_details(hashId):
    headers = {
        "X-API-Key": API_KEY,
        "User-Agent": "job-detail-fetcher"
    }

    detail_url = f"https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v2/jobdetails/{hashId}"

    response = requests.get(detail_url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_and_display_latest_job_detail(keyword, location=""):
    latest_job = get_latest_job(keyword, location)

    if latest_job is None:
        return

    hashId = latest_job.get("hashId")
    if not hashId:
        print(" hashId missing from the response, cannot fetch detailed job info.")
    return

    job_details = get_job_details(hashId)

    # Extract key details
    job_info = {
        "Job Title": job_details.get("titel"),
        "Company": job_details.get("arbeitgeber"),
        "Location": ', '.join([ort.get("ort", "N/A") for ort in job_details.get("arbeitsorte", [])]),
        "Branch": job_details.get("branche"),
        "Employment Type": job_details.get("angebotsart"),
        "Contract": job_details.get("befristung"),
        "Salary": job_details.get("verguetung"),
        "Published On": job_details.get("aktuelleVeroeffentlichungsdatum"),
        "Modified On": job_details.get("modifikationsTimestamp"),
        "Job Description": job_details.get("stellenbeschreibung"),
        "Reference Number": job_details.get("refnr"),
        "Job URL": f"https://jobboerse.arbeitsagentur.de/vamJB/{hashId}"
    }

    # Display neatly using pandas
    job_df = pd.DataFrame(job_info.items(), columns=["Field", "Detail"])
    pd.set_option('display.max_colwidth', None)
    print(job_df.to_string(index=False))

if __name__ == "__main__":
    keyword = input("Enter job title keyword (in German, e.g., Data Scientist): ")
    location = input("Enter location (optional): ")
    fetch_and_display_latest_job_detail(keyword, location)
