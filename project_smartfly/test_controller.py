import asyncio
import configs as c
from tools import RemoteController
from logger import logger

async def test_controller():
    print("Remote Controller Test Interface")
    print("-------------------------------")
    
    # Initialize the controller with test mode option
    controller = RemoteController(
        bluetooth_port=c.BLUETOOTH_PORT,
        baud_rate=c.BAUD_RATE
    )
    
    while True:
        print("\nAvailable Commands:")
        print("1. Move Forward")
        print("2. Move Backward")
        print("3. Turn Left")
        print("4. Turn Right")
        print("5. Stop")
        print("6. Set Speed")
        print("7. Exit")
        
        choice = input("\nEnter command number: ")
        
        if choice == "7":
            print("Exiting test interface...")
            break
            
        try:
            if choice in ["1", "2", "3", "4"]:
                duration = float(input("Enter duration in seconds: "))
                
                if choice == "1":
                    await controller.forward(duration)
                elif choice == "2":
                    await controller.backward(duration)
                elif choice == "3":
                    await controller.left(duration)
                elif choice == "4":
                    await controller.right(duration)
                    
            elif choice == "5":
                controller.stop()
                
            elif choice == "6":
                speed = int(input("Enter speed (0-9): "))
                if 0 <= speed <= 9:
                    controller.set_speed(speed)
                else:
                    print("Speed must be between 0 and 9")
                    
            else:
                print("Invalid command number")
                
        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error during command execution: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_controller())
    except KeyboardInterrupt:
        print("\nTest interface terminated by user")
    except Exception as e:
        print(f"\nTest interface terminated due to error: {e}")