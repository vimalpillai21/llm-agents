from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class Coder():
    """Coder crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            verbose=True,
            # allow_code_execution=True,
            # max_execution_time=30,
            # code_execution_mode="safe",
            # max_retry_limit=3
            )
    
    @task
    def coding_task(self) -> Task:
        return Task(config=self.tasks_config["coding_task"])
    

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )