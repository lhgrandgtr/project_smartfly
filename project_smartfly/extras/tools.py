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
        self.timeout = timeout
        self.command_lock = asyncio.Lock()
        self.connect()

    def connect(self):
        """Establish connection to the Bluetooth device"""
        try:
            if hasattr(self, 'bt') and self.bt is not None:
                self.bt.close()
                time.sleep(0.5)  # Wait for port to fully close
                
            self.bt = serial.Serial(
                port=self.bluetooth_port,
                baudrate=self.baud_rate,
                timeout=2,        # Increased from 1 to 2
                write_timeout=2,  # Increased from 1 to 2
                xonxoff=True,    # Enable software flow control
                rtscts=False,    # Disable hardware flow control
                dsrdtr=False,    # Disable hardware flow control
                inter_byte_timeout=1  # Add timeout between bytes
            )
            # Attempt to reset the device
            self.bt.reset_input_buffer()
            self.bt.reset_output_buffer()
            time.sleep(1)  # Wait for connection to stabilize
            logger.info(f"Connected to {self.bluetooth_port} at {self.baud_rate} baud.")
            return True
        except serial.SerialException as e:
            logger.error(f"Could not connect to Bluetooth device: {e}")
            self.bt = None
            return False

    def send_command(self, command: str):
        """Send command with automatic reconnection attempt on failure"""
        if self.bt is None and not self.connect():
            logger.error("Bluetooth connection not established.")
            return False
            
        try:
            # Add a small delay between commands
            time.sleep(0.02)
            self.bt.write(command.encode())
            self.bt.flush()  # Ensure data is written
            logger.debug(f"Sent command: {command}")
            return True
        except (serial.SerialTimeoutException, serial.SerialException) as e:
            logger.error(f"Failed to send command: {command}, error: {e}")
            if "timeout" in str(e).lower() or "input/output error" in str(e).lower():
                logger.info("Attempting to reconnect...")
                if self.connect():
                    try:
                        self.bt.write(command.encode())
                        self.bt.flush()
                        logger.debug(f"Sent command after reconnection: {command}")
                        return True
                    except serial.SerialException as e2:
                        logger.error(f"Failed to send command after reconnection: {e2}")
            return False
    

    @kernel_function(
        name="move_forward",
        description="Move the car forward for a specified time period",
    )
    def forward(self, period: str) -> str:
        """Move forward for a specified period."""
        logger.info("Moving forward")
        try:
            period_float = float(period)
            logger.debug(f"Moving forward for: {period_float} seconds")
            
            start_time = time.time()
            command_interval = 0.1  # Send command every 100ms
            last_command_time = 0
            
            while (time.time() - start_time) < period_float:
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    self.send_command('U')
                    last_command_time = current_time
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            
            self.stop()
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
    def backward(self, period: str) -> str:
        """Move backward for a specified period."""
        logger.info("Moving backward")
        try:
            period_float = float(period)
            logger.debug(f"Moving backward for: {period_float} seconds")
            
            start_time = time.time()
            command_interval = 0.1  # Send command every 100ms
            last_command_time = 0
            
            while (time.time() - start_time) < period_float:
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    self.send_command('D')
                    last_command_time = current_time
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            
            self.stop()
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
    def left(self, period: str) -> str:
        """Turn left for a specified period."""
        logger.info("Turning left")
        try:
            period_float = float(period)
            logger.debug(f"Turning left for: {period_float} seconds")
            
            start_time = time.time()
            command_interval = 0.1  # Send command every 100ms
            last_command_time = 0
            
            while (time.time() - start_time) < period_float:
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    self.send_command('L')
                    last_command_time = current_time
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            
            self.stop()
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
    def right(self, period: str) -> str:
        """Turn right for a specified period."""
        logger.info("Turning right")
        try:
            period_float = float(period)
            logger.debug(f"Turning right for: {period_float} seconds")
            
            start_time = time.time()
            command_interval = 0.1  # Send command every 100ms
            last_command_time = 0
            
            while (time.time() - start_time) < period_float:
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    self.send_command('R')
                    last_command_time = current_time
                time.sleep(0.01)  # Small sleep to prevent CPU hogging
            
            self.stop()
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
    def stop(self) -> str:
        """Stop the car."""
        logger.info("Stopping")
        self.send_command('X')
        logger.info("Stopped")
        return 'Stop complete'

    @kernel_function(
        name="set_car_speed",
        description="Set the speed of the car (value between 0-9)",
    )
    def set_speed(self, speed: str) -> str:
        """Set the speed of the car."""
        try:
            speed_int = int(speed)
            if speed_int < 0 or speed_int > 9:
                logger.error("Speed must be an integer between 0 and 9.")
                return "Error: Speed must be between 0 and 9"
            logger.info(f"Setting speed to {speed_int}")
            self.send_command(str(speed_int))
            logger.info("Speed set")
            return f'Speed set to {speed_int}'
        except ValueError as e:
            error_msg = f"Invalid speed value: {speed}, error: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'


if __name__ == "__main__":
    controller = RemoteController()
