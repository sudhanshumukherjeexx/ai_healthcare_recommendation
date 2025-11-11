import argparse
from rec_engine import build_recommendations
import json

def main():
    parser = argparse.ArgumentParser(description="AI Recommendation Agent (CLI)")
    parser.add_argument("--userid", "-u", required=True, help="USERID to generate recommendations for")
    args = parser.parse_args()

    result = build_recommendations(args.userid)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
