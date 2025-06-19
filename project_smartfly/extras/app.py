import asyncio
from semantic_kernel import Kernel
import configs as c
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from semantic_kernel.connectors.ai.google.google_ai.google_ai_prompt_execution_settings import (
    GoogleAIPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory, ChatMessageContent, TextContent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

import threading
import cv2

import web_server
from tools import RemoteController
from vision import VisionAnalyzer
from logger import logger

async def main():
    kernel = Kernel()
    history = ChatHistory()
    
    # Single system message for navigation
    history.add_system_message(
        "You are an AI system controlling a toy car. Available commands:\n"
        "- forward(period): Move forward for specified seconds\n"
        "- backward(period): Move backward for specified seconds\n"
        "- left(period): Turn left for specified seconds\n"
        "- right(period): Turn right for specified seconds\n"
        "- stop(): Stop all movement\n"
        "- set_speed(speed): Set speed (0-9)\n\n"
        "Make decisions based on the vision analysis provided."
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
    kernel.add_plugin(controller)

    # Initialize vision analyzer
    vision_analyzer = VisionAnalyzer()

    # Start web server
    web_thread = threading.Thread(target=web_server.start_server, daemon=True)
    web_thread.start()
    logger.info(f"Web server started on {c.SERVER_URL}")

    try:
        async for analysis_result in vision_analyzer.start_stream_analysis():
            frame = analysis_result['frame']
            analysis = analysis_result['analysis']
            
            # Update web interface
            web_server.update_frame(frame)
            web_server.update_thoughts(analysis)
            
            # Add vision analysis as user message for context
            history.add_message(
                ChatMessageContent(
                    role="user",
                    items=[TextContent(text=f"Vision Analysis: {analysis}")]
                )
            )
            
            # Get navigation decision based on vision analysis
            response = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel
            )
            
            # Execute navigation command if any
            command_str = str(response)
            logger.info(f"Navigation command: {command_str}")
            web_server.update_thoughts(f"Executing: {command_str}")
            
            # Update vision analyzer with the executed command
            vision_analyzer.update_last_movement(command_str)

            # Add the response to history as assistant message
            history.add_message(
                ChatMessageContent(
                    role="assistant",
                    items=[TextContent(text=command_str)]
                )
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Exit command received. Exiting loop.")
                break
                
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
    finally:
        logger.info("Program terminated.")

if __name__ == "__main__":
    asyncio.run(main())