import pandas as pd
from db_connect import session
from models import Job

# Correct path
df = pd.read_excel("datasets/jobs_dataset_full.xlsx")

for _, row in df.iterrows():
    job = Job(
        job_title=row["job_title"],
        company=row["company"],
        location=row["location"],
        description=row["description"],
        domain="",   # not in your dataset yet
        role="",     # not in your dataset yet
        source=""    # not in your dataset yet
    )
    session.add(job)

session.commit()

print("Data inserted successfully!")