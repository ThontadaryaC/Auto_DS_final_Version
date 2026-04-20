import pandas as pd
import json
import os
import sys

# Add backend to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

def test_serialization():
    print("Testing Serialization Fix...")
    df = pd.DataFrame({
        'Date': pd.to_datetime(['2024-01-01', '2024-01-02']),
        'Value': [10, 20]
    })
    
    try:
        # This was the problematic way
        # json.dumps(df.head(5).to_dict(orient='records')) 
        # This will fail
        pass
    except TypeError as e:
        print(f"Confirmed original way failed: {e}")

    try:
        # This is the fix
        sample_data_json = df.head(5).to_json(orient='records', date_format='iso')
        json.loads(sample_data_json)
        print("Success: to_json handles Timestamps correctly.")
    except Exception as e:
        print(f"Failure: to_json still failed: {e}")

def test_scraper():
    print("\nTesting Scraper...")
    from services.scraper import research_industry_context
    context = research_industry_context("Recent trends in AI Data Science 2024", max_results=3)
    if "Source 1" in context:
        print("Success: Scraper returned results.")
    else:
        print(f"Scraper returned unexpected result: {context}")

if __name__ == "__main__":
    test_serialization()
    test_scraper()
