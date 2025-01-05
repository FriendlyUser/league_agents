from crewai.tools import BaseTool
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import gdown

league_file_path = 'league_pro_games.csv'

def download_csv():
    """
    Downloads the CSV file from Google Drive if the local file has not
    been updated within the last 24 hours. Otherwise, it skips downloading.
    The downloaded file is saved to `self.file_path`.
    """

    def is_file_updated_within_24_hours(file_path):
        """
        Checks if a file at the given path has been modified within
        the last 24 hours.
        
        Args:
            file_path (str): The path to the file.
        
        Returns:
            bool: True if the file exists and has been updated within
                    the last 24 hours, False otherwise.
        """
        if os.path.exists(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            return datetime.now() - file_mod_time < timedelta(hours=24)
        return False

    file_url = 'https://drive.google.com/uc?id=1IjIEhLc9n8eLKeY-yh_YigKVWbhgGBsN'

    if not is_file_updated_within_24_hours(league_file_path):
        gdown.download(file_url, league_file_path, quiet=False)
        print("File downloaded successfully.")
    else:
        print("File is up to date.")

class PlayerResultsTool(BaseTool):
    name: str = "player_results"
    description: str = (
        "A utility class that downloads and processes League of Legends professional "
        "match data from https://oracleselixir.com/, focusing on esports and "
        "professional gaming matches. The data provides insights into player performance, "
        "including statistics like kills, deaths, assists, dragons, barons, "
        "gold differences, and more."
    )
    file_path: str = league_file_path

    

    def _run(self, team1: str, team2: str) -> str:
        # if self
        if not os.path.exists(league_file_path):
            download_csv()
        else:
            print("File already exists.")
        df = pd.read_csv(self.file_path)
        filtered_df = df[(df['teamname'] == team1) | (df['teamname'] == team2)]

        # comparison = filtered_df.groupby(['teamname'])
        # take the last 50 rows
        # should be last 5 games for each team.
        comparison = filtered_df.tail(50)
        return comparison.to_string()

    def filter_teams(self, team1, team2):
        """
        Filters the dataset for the specified teams and returns a summary of
        average kills, deaths, assists, dragons, and barons grouped by
        team name and champion.

        Args:
            team1 (str): Name of the first team to filter.
            team2 (str): Name of the second team to filter.

        Returns:
            str: A string representation of the filtered DataFrame summary.
        """
        df = pd.read_csv(self.file_path)
        filtered_df = df[(df['teamname'] == team1) | (df['teamname'] == team2)]

        summary = filtered_df.groupby(['teamname', 'champion'])[
            ['kills', 'deaths', 'assists', 'dragons', 'barons']
        ].mean().reset_index()

        return summary.to_string()


    def compare_teams(self, team1, team2):
        """
        Compares performance metrics between the two specified teams, including
        average gold differences at 15 and 25 minutes, and rates of securing
        first baron and first dragon.

        Args:
            team1 (str): Name of the first team to compare.
            team2 (str): Name of the second team to compare.

        Returns:
            str: A string representation of the comparison metrics
                 DataFrame for the two teams.
        """
        df = pd.read_csv(self.file_path)
        filtered_df = df[(df['teamname'] == team1) | (df['teamname'] == team2)]

        comparison = filtered_df.groupby(['teamname'])[
            ['golddiffat15', 'golddiffat25', 'firstbaron', 'firstdragon']
        ].mean().reset_index()

        return comparison.to_string()

class TeamComparisonTool(BaseTool):
    name: str = "player_results"
    description: str = (
        "A utility class that downloads and processes League of Legends professional "
        "match data from https://oracleselixir.com/, focusing on esports and "
        "professional gaming matches. The data provides insights into team performance, "
        "including statistics like kills, deaths, assists, dragons, barons, "
        "gold differences, and more."
    )
    file_path: str = league_file_path

    

    def _run(self, team1: str, team2: str) -> str:
        """
        Filters the dataset for the specified teams and returns a summary of
        average kills, deaths, assists, dragons, and barons grouped by
        team name and champion.

        Args:
            team1 (str): Name of the first team to filter.
            team2 (str): Name of the second team to filter.

        Returns:
            str: A string representation of the filtered DataFrame summary.
        """
        df = pd.read_csv(self.file_path)
        filtered_df = df[(df['teamname'] == team1) | (df['teamname'] == team2)]

        summary = filtered_df.groupby(['teamname', 'champion'])[
            [
                'kills', 'deaths', 'assists', 'dragons', 'barons',
                'goldat10', 'goldat15', 'goldat20', 'golddiffat10', 'golddiffat15', 'golddiffat20',
                'firstdragon', 'firstbaron', 'firsttower', 'towers', 'inhibitors',
                'damagetochampions', 'damageshare', 'earnedgold', 'earned gpm'
            ]
        ].mean().reset_index()

        return summary.to_string()