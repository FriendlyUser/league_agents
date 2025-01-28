#!/usr/bin/env python
import sys
import warnings

from league_agents.crew import LeagueAgents

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'team1': 'OKSavingsBank BRION',
        'team2': 'Dplus Kia', 
    }
    # inputs = {
    #     'team1': 'T1',
    #     'team2': 'Gen.G', 
    # }
    # inputs = {
    #     'team1': 'KT Rolster',
    #     'team2': 'BNK FearX',
    # }
    # inputs = {
    #     'team1': 'Dplus KIA',
    #     'team2': 'T1',
    # }
    LeagueAgents().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'team1': 'OKSavingsBank BRION',
        'team2': 'Dplus KIA', 
    }
    try:
        LeagueAgents().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LeagueAgents().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        LeagueAgents().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
