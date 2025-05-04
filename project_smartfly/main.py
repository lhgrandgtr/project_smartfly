import configs as c

import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from semantic_kernel.connectors.ai.google.google_ai.google_ai_prompt_execution_settings import (
    GoogleAIPromptExecutionSettings,
)

from semantic_kernel.contents import ChatHistory, ChatMessageContent, ImageContent, TextContent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from tools import RemoteController
from logger import logger


async def main():
    print("Hello from project-smartfly!")
    kernel = Kernel()
    history = ChatHistory()
    history.add_system_message(
        "You are a navigation system for a toy car. You must format your responses as a sequence of commands without any other text.\n"
        "Available commands:\n"
        "forward(period)\n"
        "backward(period)\n"
        "left(period)\n"
        "right(period)\n"
        "stop()\n"
        "set_speed(speed)\n\n"
        "Example multi-step command response format:\n"
        "forward(3)\n"
        "left(2)\n"
        "forward(1)\n"
        "Do not include any other text, just the commands to execute."
    )

    chat_completion = GoogleAIChatCompletion(
        gemini_model_id="gemini-2.0-flash",
        api_key=c.GOOGLE_API_KEY,
    )

    kernel.add_service(chat_completion)

    execution_settings = GoogleAIPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Required()
    execution_settings.temperature = 0.1
    execution_settings.candidate_count = 1

    controller = RemoteController(
        bluetooth_port=c.BLUETOOTH_PORT,
        baud_rate=c.BAUD_RATE,
    )
    kernel.add_plugin(controller, plugin_name='controller')

    while True:
        user_input = input("User > ")
        if user_input.lower() == "exit":
            break

        history.add_message(
            ChatMessageContent(
                role="user",
                items=[TextContent(text=user_input)]
            )
        )

        try:
            # Get the command sequence from the AI
            chat_response = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )

            # Extract commands from the response
            response_text = chat_response.value if hasattr(chat_response, 'value') else str(chat_response)
            commands = []
            
            # Parse and execute each command in sequence
            for command in response_text.strip().split('\n'):
                if command.strip():  # Skip empty lines
                    await getattr(controller, command.split('(')[0])(
                        command.split('(')[1].split(')')[0]
                    )
                    await asyncio.sleep(0.1)  # Small delay between commands

            # Add the response to the history
            history.add_message(chat_response)
            print("All commands completed successfully")

        except Exception as e:
            logger.error(f"Error executing commands: {str(e)}")
            print(f"Error executing commands: {str(e)}")
            continue

if __name__ == "__main__":
    asyncio.run(main())
