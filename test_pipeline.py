# test_pipeline.py

from newsapi import run_pipeline

if __name__ == "__main__":
    API_TOKEN = "MD9SRQGgfM8S8pmV3pxCFaP51x94WtB6C5iwPlSo"

    # Run pipeline for Fortune 500 companies
    run_pipeline(API_TOKEN, limit=3)
