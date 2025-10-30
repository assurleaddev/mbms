#!/usr/bin/env python
import warnings

from datetime import datetime

from crewai import CrewOutput
from crew import DemoProject
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(prompt) -> CrewOutput:
    """
    Run the crew.
    """
    inputs = {
        'prompt': prompt,
        'current_year': str(datetime.now().year)
    }
    
    try:
        return DemoProject().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def main():
    prompt = input('Enter your prompt: ')
    run(prompt)


if __name__ == '__main__':
    main()
