#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import os

from financial_researcher.crew import ResearcherCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


os.makedirs("output",exist_ok=True)

def run():
    """Run the research crew"""

    inputs = {
        "company": "Tesla"
    }

    result = ResearcherCrew().crew().kickoff(inputs=inputs)

    print("\n\n Final Report \n\n")
    print(result.raw)
    print("\n\nReport has been saved to output/report2.md")


if __name__ == "__main__":
    run() 