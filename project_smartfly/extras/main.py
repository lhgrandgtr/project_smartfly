import configs as c


from tools import RemoteController
from logger import logger
from crewai import Agent, LLM




def main():
    logger.info("Initializing the navigation system...")

    llm = LLM(
        model="gemini-2.0-flash",
        api_key=c.GOOGLE_API_KEY,
        temperature=0.1,
    )

    cruise_navigator= Agent(
        role="You are a navigator that helps a toy car navigate through an environment. You have access to a vision tool that can analyze the environment and provide insights.",
        goal="Analyze the environment and provide navigation instructions to the car controller.",
        llm=llm,
        tools=[],
        verbose=True
    )


if __name__ == "__main__":
    main()
