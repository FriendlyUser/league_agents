from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    WebsiteSearchTool,
    YoutubeChannelSearchTool
)
import os
from .tools.csv_data_tool import PlayerResultsTool, TeamComparisonTool

gemini_api_key = os.getenv("GEMINI_API_KEY")
player_result_tool = PlayerResultsTool()
team_comparison_tool = TeamComparisonTool()

lck_video_tool = YoutubeChannelSearchTool(
    youtube_channel_handle="@oplolreplay",
    config=dict(
        embedder={
            "provider": "google",
            "config": {
                "model":  "models/text-embedding-004"
            }
        }
    )
)


docs_tool = DirectoryReadTool(directory='./data/games/')
file_tool = FileReadTool()
web_rag_tool = WebsiteSearchTool(
    website='https://www.leagueoflegends.com/en-us/news/tags/patch-notes/',
    config=dict(

        embedder={
            "provider": "google",
            "config": {
                "model":  "models/text-embedding-004"
            }
        }
    )
)




lol_fandom = WebsiteSearchTool(
    website='https://lol.fandom.com//',
    config=dict(
        embedder=dict(
            provider="google", # or openai, ollama, ...
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )

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
            embedder={
                "provider": "google",
                "config": {
                    "api_key": gemini_api_key,
                    "model":  "models/text-embedding-004", 
                }
            }
        )

    # grab the transcript of the video separately and dump to a text file?
    # lol fandom is uneeded
    @agent
    def meta_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["meta_analyst"],
            tools=[docs_tool, file_tool],
            verbose=True,
             embedder={
                "provider": "google",
                "config": {
                    "api_key": gemini_api_key,
                    "model":  "models/text-embedding-004", 
                }
            }
        )

    @agent
    def lead_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_analyst"],
            tools=[team_comparison_tool],
            verbose=True,
             embedder={
                "provider": "google",
                "config": {
                    "api_key": gemini_api_key,
                    "model":  "models/text-embedding-004", 
                }
            }
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
            max_rpm = 2,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": api_key,
                    "model":  "models/text-embedding-004", 
                }
            }
        )
