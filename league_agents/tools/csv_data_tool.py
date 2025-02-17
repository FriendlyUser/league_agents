from crewai.tools import BaseTool
import pandas as pd
import os
from data_downloader import download_csv, LEAGUE_FILE_PATH # Import the function and constant
# from data_downloader import download_csv # Import the function


class PlayerResultsTool(BaseTool):
    name: str = "player_results"
    description: str = (
        "A utility class that downloads and processes League of Legends professional "
        "match data from https://oracleselixir.com/, focusing on esports and "
        "professional gaming matches. The data provides insights into player performance, "
        "including statistics like kills, deaths, assists, dragons, barons, "
        "gold differences, and more."
    )
    file_path: str = LEAGUE_FILE_PATH

    def _run(self, team1: str, team2: str) -> str:
        if not os.path.exists(LEAGUE_FILE_PATH):
            download_csv(LEAGUE_FILE_PATH)
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
    name: str = "team_comparison"  # changed name
    description: str = (
        "A utility class that downloads and processes League of Legends professional "
        "match data from https://oracleselixir.com/, focusing on esports and "
        "professional gaming matches. The data provides insights into team performance, "
        "including statistics like kills, deaths, assists, dragons, barons, "
        "gold differences, and more."
    )
    file_path: str = LEAGUE_FILE_PATH

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
        if not os.path.exists(LEAGUE_FILE_PATH):
            download_csv(LEAGUE_FILE_PATH)
        else:
            print("File already exists.")

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