import asyncio
import serial
import time
from typing import Optional
from crewai.tools import BaseTool
from src.utils.logger import logger

class RemoteControlTool(BaseTool):
    name: str = "Remote Control Tool"
    description: str = "Controls a remote car via Bluetooth for movement and speed adjustments"

    def __init__(self, bluetooth_port: str, baud_rate: int, timeout: int = 1):
        super().__init__()
        logger.info("Initializing RemoteControlTool ...")
        self.bluetooth_port = bluetooth_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.command_lock = asyncio.Lock()
        self.bt = None
        self._connect()

    def _connect(self):
        """Private method to establish connection to the Bluetooth device"""
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

    def _send_command(self, command: str):
        """Private method to send commands with automatic reconnection"""
        if self.bt is None and not self._connect():
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
                if self._connect():
                    try:
                        self.bt.write(command.encode())
                        self.bt.flush()
                        logger.debug(f"Sent command after reconnection: {command}")
                        return True
                    except serial.SerialException as e2:
                        logger.error(f"Failed to send command after reconnection: {e2}")
            return False

    def _execute_timed_command(self, command: str, period: float, command_char: str) -> str:
        """Private method to execute a timed movement command"""
        logger.info(f"Executing {command}")
        try:
            logger.debug(f"Movement duration: {period} seconds")
            
            start_time = time.time()
            command_interval = 0.1
            last_command_time = 0
            
            while (time.time() - start_time) < period:
                current_time = time.time()
                if current_time - last_command_time >= command_interval:
                    self._send_command(command_char)
                    last_command_time = current_time
                time.sleep(0.01)
            
            self._stop()
            logger.info(f"Stopped {command}")
            return f'{command} complete'
        except Exception as e:
            error_msg = f"Error during {command}: {str(e)}"
            logger.error(error_msg)
            return f'Error: {error_msg}'

    def _stop(self) -> str:
        """Private method to stop movement"""
        logger.info("Stopping")
        self._send_command('X')
        logger.info("Stopped")
        return 'Stop complete'

    def _set_speed(self, speed: int) -> str:
        """Private method to set speed"""
        if not (0 <= speed <= 9):
            error_msg = "Speed must be between 0 and 9"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        logger.info(f"Setting speed to {speed}")
        self._send_command(str(speed))
        logger.info("Speed set")
        return f'Speed set to {speed}'

    def run(
        self,
        command: str,
        duration: Optional[float] = None,
        speed: Optional[int] = None
    ) -> dict:
        """
        Execute remote control commands.
        
        Args:
            command: Movement command ('forward', 'backward', 'left', 'right', 'stop')
            duration: Duration in seconds for movement commands
            speed: Speed setting (0-9)
        """
        try:
            result = {}
            
            if speed is not None:
                result['speed_change'] = self._set_speed(speed)

            if command == 'stop':
                result['movement'] = self._stop()
            elif duration is not None:
                command_map = {
                    'forward': ('Forward', 'U'),
                    'backward': ('Backward', 'D'),
                    'left': ('Left turn', 'L'),
                    'right': ('Right turn', 'R')
                }
                
                if command in command_map:
                    name, char = command_map[command]
                    result['movement'] = self._execute_timed_command(name, duration, char)
                else:
                    raise ValueError(f"Unknown command: {command}")
            else:
                raise ValueError("Duration required for movement commands")

            return result

        except Exception as e:
            raise Exception(f"Error in remote control: {str(e)}")

    def describe(self) -> str:
        return """
        This tool controls a remote car via Bluetooth and can:
        - Move forward/backward
        - Turn left/right
        - Stop movement
        - Set speed
        
        Parameters:
        - command: Movement type ('forward', 'backward', 'left', 'right', 'stop')
        - duration: Time in seconds for movement
        - speed: Speed setting (0-9)
        """

if __name__ == "__main__":
    controller = RemoteControlTool(bluetooth_port="/dev/ttyUSB0", baud_rate=9600)
