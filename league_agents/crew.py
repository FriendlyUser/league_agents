from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    WebsiteSearchTool
)
import os
from .tools.csv_data_tool import PlayerResultsTool, TeamComparisonTool

player_result_tool = PlayerResultsTool()
team_comparison_tool = TeamComparisonTool()

docs_tool = DirectoryReadTool(directory='./data')
file_tool = FileReadTool()
web_rag_tool = WebsiteSearchTool(
    website='https://www.leagueoflegends.com/en-us/news/tags/patch-notes/',
    embedder=dict(
        provider="google", # or openai, ollama, ...
        config=dict(
            model="models/embedding-001",
            task_type="retrieval_document",
            # title="Embeddings",
        ),
    ),
)

lol_fandom = WebsiteSearchTool(
    website='https://lol.fandom.com//',
      embedder=dict(
        provider="google", # or openai, ollama, ...
        config=dict(
            model="models/embedding-001",
            task_type="retrieval_document",
            # title="Embeddings",
        ),
    ),
)

@CrewBase
class LeagueAgents:
    """League Analysis Crew"""

    agents_config = "config/agents_league.yaml"
    tasks_config = "config/agents_tasks.yaml"

    @agent
    def team_performance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["team_performance_analyst"],
            tools=[player_result_tool],
            verbose=True,
        )

    @agent
    def meta_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_analyst"],
            tools=[docs_tool, file_tool, web_rag_tool, lol_fandom],
            verbose=True,
        )

    @agent
    def lead_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_analyst"],
            tools=[team_comparison_tool],
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
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GOOGLE_MODEL_NAME")
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # https://ai.google.dev/pricing#1_5flash
            max_rpm = 15,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": api_key,
                    "model_name":   model_name, 
                }
            }
        )
