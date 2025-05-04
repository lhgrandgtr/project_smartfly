import asyncio
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig
import configs as c
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from semantic_kernel.connectors.ai.google.google_ai.google_ai_prompt_execution_settings import (
    GoogleAIPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory, ChatMessageContent, ImageContent, TextContent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

import threading
import cv2

import web_server
from tools import RemoteController
from logger import logger

async def main():
    kernel = Kernel()
    history = ChatHistory()
    history.add_system_message(
        "You are a navigation system for a toy car. You can control the car using these functions:\n"
        "- forward(period): Move forward for specified seconds\n"
        "- backward(period): Move backward for specified seconds\n"
        "- left(period): Turn left for specified seconds\n"
        "- right(period): Turn right for specified seconds\n"
        "- stop(): Stop all movement\n"
        "- set_speed(speed): Set speed (0-9)\n\n"
        "IMPORTANT: For multi-step commands like 'move forward 3s, turn left 2s, move forward 1s':\n"
        "1. Execute all commands in a single response\n"
        "2. Do not add text between commands\n"
        "3. Example format:\n"
        "   forward(3)\n"
        "   left(2)\n"
        "   forward(1)\n"
        "4. Wait for each command to complete before starting the next\n"
        "5. Only report completion after all commands are done"
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

    web_thread = threading.Thread(target=web_server.start_server, daemon=True)
    web_thread.start()
    logger.info(f"Web server started on {c.SERVER_URL}")

    cap = cv2.VideoCapture(c.VIDEO_URL)
    if not cap.isOpened():
        logger.error("Failed to open video capture.")
        return
    logger.info("Video capture started.")

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("No frame retrieved. Exiting loop.")
                break

            if frame_count % c.FRAME_INTERVAL == 0:
                try:
                    saved = cv2.imwrite(c.FRAME_PATH, frame)
                    if not saved:
                        logger.error("Failed to save frame")
                        continue
                        
                    web_server.update_frame(frame)
                    history.add_message(
                        ChatMessageContent(
                            role="user",
                            items=[
                                TextContent(text="Please describe the current scene and any obstacles with directions relative to the toy car."),
                                ImageContent.from_image_file(path=c.FRAME_PATH),
                            ]
                        )
                    )
                    
                    response = await chat_completion.get_chat_message_content(
                        chat_history=history,
                        settings=execution_settings,
                        kernel=kernel,
                    )
                    
                    logger.info(f"AI Response: {str(response)}")
                    web_server.update_thoughts(str(response))
                except Exception as e:
                    logger.error(f"Error processing frame: {str(e)}")

            frame_count += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Exit command received. Exiting loop.")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Program terminated.")

if __name__ == "__main__":
    asyncio.run(main())