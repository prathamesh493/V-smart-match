# app/observability/metrics.py
from prometheus_client import Counter

# Define all custom metrics here so they can be imported anywhere.
resumes_processed_total = Counter(
    "vsmart_resumes_processed_total",
    "Total number of resumes successfully processed."
)