from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
from src.tools.vision import VisionNavigationTool
from src.tools.remote import RemoteControlTool
from src.utils import logger


@CrewBase
class NavigationCrew():
    """NavigationCrew"""

    agents_config = "config/agents.yaml"

    @agent
    def car_controller(self) -> Agent:
        return Agent(
        config=self.agents_config['car_controller'],
        verbose=True,
        tools=[VisionNavigationTool, RemoteControlTool]
        )
    
    @task
    def navigate_task(self) -> Task:
        return Task(
        config=self.tasks_config['navigate_task'] 
        )

    @task
    def control_task(self) -> Task:
        return Task(
        config=self.tasks_config['control_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew( 
            memory=True,        
            agents=[
                self.car_controller()
            ],
            tasks=[
                self.navigate_task(),
                self.control_task()
            ],
            process=Process.sequential
        )