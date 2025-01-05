from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

from .tools.csv_data_tool import CSVDataTool

csv_data_tool = CSVDataTool()

@CrewBase
class LeagueAgents:
    """League Analysis Crew"""

    agents_config = "config/agents_league.yaml"
    tasks_config = "config/agents_tasks.yaml"

    @agent
    def team_performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["team_performance_analyst"],
            tools=[csv_data_tool],
            verbose=True,
        )

    @agent
    def meta_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_analyst"],
            tools=[csv_data_tool],
            verbose=True,
        )

    @agent
    def lead_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_analyst"],
            tools=[csv_data_tool],
            verbose=True,
        )

    @task
    def analyze_team_performance(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_team_performance"],
        )

    @task
    def track_meta_shifts(self) -> Task:
        return Task(
            config=self.tasks_config["track_meta_shifts"],
        )

    @task
    def final_prediction_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_prediction_task"],
            output_file="prediction_report.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
