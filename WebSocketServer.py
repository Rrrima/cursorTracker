import asyncio
import websockets
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BrowserTracker')

class BrowserTracker:
    def __init__(self, callback):
        self.callback = callback
        self.server = None
        
    async def handle_messages(self, websocket):
        client_id = id(websocket)
        logger.info(f"New client connected: {client_id}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data['type'] == 'element_data':
                        element_data = data['data']
                        element_data['timestamp'] = datetime.now().strftime('%m%d_%H%M%S')
                        logger.debug(f"Received data from {client_id}: {element_data['tagName']}")
                        self.callback(element_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
    async def start_server(self):
        try:
            self.server = await websockets.serve(
                self.handle_messages, 
                "localhost", 
                8765
            )
            logger.info("WebSocket server started on ws://localhost:8765")
            await self.server.wait_closed()
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
        
    def start(self):
        logger.info("Starting WebSocket server...")
        asyncio.run(self.start_server())
        
    def stop(self):
        if self.server:
            self.server.close()
            logger.info("WebSocket server stopped") 