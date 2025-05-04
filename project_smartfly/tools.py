import asyncio
import serial
import time
from semantic_kernel.functions import kernel_function
from logger import logger


class RemoteController:
    def __init__(self, bluetooth_port, baud_rate, timeout=1):
        logger.info("Initializing RemoteController ...")
        self.bluetooth_port = bluetooth_port
        self.baud_rate = baud_rate
        self.command_lock = asyncio.Lock()  # Add lock for sequential execution
        try:
            self.bt = serial.Serial(port=bluetooth_port, baudrate=baud_rate, timeout=timeout)
            logger.info(f"Connected to {bluetooth_port} at {baud_rate} baud.")
        except serial.SerialException as e:
            logger.error(f"Could not connect to Bluetooth device: {e}")
            self.bt = None

    async def send_command(self, command):
        if self.bt is None:
            logger.error("Bluetooth connection not established.")
            return
        async with self.command_lock:  # Use lock to ensure sequential execution
            self.bt.write(command.encode())
            logger.debug(f"Sent command: {command}")
            await asyncio.sleep(0.01)  # Small delay between commands

    async def execute_sequence(self, commands):
        """Execute a sequence of commands in order"""
        for cmd, args in commands:
            await getattr(self, cmd)(*args)
            await asyncio.sleep(0.1)  # Small delay between commands

    def _extract_value(self, period):
        """Helper method to extract value from MapComposite or similar objects."""
        logger.debug(f"Extracting value from period: {type(period)}")
        
        try:
            # If it's already a number or numeric string, convert and return it
            if isinstance(period, (int, float)):
                return float(period)
            if isinstance(period, str):
                # First try direct conversion
                try:
                    return float(period)
                except ValueError:
                    # Extract numbers from the string if direct conversion fails
                    import re
                    numbers = re.findall(r'\d*\.?\d+', period)
                    if numbers:
                        return float(numbers[0])
            
            # Handle various object types that might contain the value
            for attr in ["content", "value", "result"]:
                if hasattr(period, attr):
                    val = getattr(period, attr)
                    if val is not None:
                        return self._extract_value(val)
            
            # Handle dictionary case
            if isinstance(period, dict):
                for key in ["value", "content", "result"]:
                    if key in period:
                        return self._extract_value(period[key])
            
            raise ValueError("Could not extract a valid number")
            
        except Exception as e:
            logger.error(f"Value extraction failed: {str(e)}")
            if hasattr(period, "__dict__"):
                logger.debug(f"Period object attributes: {period.__dict__}")
            return 1.0  # Return a default value of 1.0 instead of 0.0

    @kernel_function(
        name="move_forward",
        description="Move the car forward for a specified time period",
    )
    async def forward(self, period: str) -> str:
        """Move forward for a specified period."""
        logger.info("Moving forward")
        try:
            period_float = float(period)
            logger.debug(f"Moving forward for: {period_float} seconds")
            
            start_time = time.time()
            while (time.time() - start_time) < period_float:
                await self.send_command('U')
            await self.stop()
            logger.info("Stopped moving forward")
            return 'Moving forward complete'
        except ValueError as e:
            error_msg = f"Invalid period value: {period}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'

    @kernel_function(
        name="move_backward",
        description="Move the car backward for a specified time period",
    )
    async def backward(self, period: str) -> str:
        """Move backward for a specified period."""
        logger.info("Moving backward")
        try:
            period_float = float(period)
            logger.debug(f"Moving backward for: {period_float} seconds")
            
            start_time = time.time()
            while (time.time() - start_time) < period_float:
                await self.send_command('D')
            await self.stop()
            logger.info("Stopped moving backward")
            return 'Moving backward complete'
        except ValueError as e:
            error_msg = f"Invalid period value: {period}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'

    @kernel_function(
        name="turn_left",
        description="Turn the car left for a specified time period",
    )
    async def left(self, period: str) -> str:
        """Turn left for a specified period."""
        logger.info("Turning left")
        try:
            period_float = float(period)
            logger.debug(f"Turning left for: {period_float} seconds")
            
            start_time = time.time()
            while (time.time() - start_time) < period_float:
                await self.send_command('L')
            await self.stop()
            logger.info("Stopped turning left")
            return 'Turning left complete'
        except ValueError as e:
            error_msg = f"Invalid period value: {period}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'

    @kernel_function(
        name="turn_right", 
        description="Turn the car right for a specified time period",
    )
    async def right(self, period: str) -> str:
        """Turn right for a specified period."""
        logger.info("Turning right")
        try:
            period_float = float(period)
            logger.debug(f"Turning right for: {period_float} seconds")
            
            start_time = time.time()
            while (time.time() - start_time) < period_float:
                await self.send_command('R')
            await self.stop()
            logger.info("Stopped turning right")
            return 'Turning right complete'
        except ValueError as e:
            error_msg = f"Invalid period value: {period}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'

    @kernel_function(
        name="stop_car",
        description="Stop all car movement immediately",
    )
    async def stop(self) -> str:
        """Stop the car."""
        logger.info("Stopping")
        await self.send_command('X')
        logger.info("Stopped")
        return 'Stop complete'

    @kernel_function(
        name="set_car_speed",
        description="Set the speed of the car (value between 0-9)",
    )
    async def set_speed(self, speed: str) -> str:
        """Set the speed of the car."""
        try:
            speed_int = int(speed)
            if speed_int < 0 or speed_int > 9:
                logger.error("Speed must be an integer between 0 and 9.")
                return "Error: Speed must be between 0 and 9"
            logger.info(f"Setting speed to {speed_int}")
            await self.send_command(str(speed_int))
            logger.info("Speed set")
            return f'Speed set to {speed_int}'
        except ValueError as e:
            error_msg = f"Invalid speed value: {speed}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'


if __name__ == "__main__":
    controller = RemoteController()
