import asyncio
import websockets
import json
from datetime import datetime

class BrowserTracker:
    def __init__(self, callback):
        self.callback = callback
        self.server = None
    async def handle_messages(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                if data['type'] == 'element_data':
                    # Add timestamp and process the data
                    element_data = data['data']
                    element_data['timestamp'] = datetime.now().strftime('%m%d_%H%M%S')
                    
                    # Send to main tracker
                    self.callback(element_data)
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        
    async def start_server(self):
        self.server = await websockets.serve(
            self.handle_messages, 
            "localhost", 
            8080
        )
        print("WebSocket server started on ws://localhost:8080")
        await self.server.wait_closed()
        
    def start(self):
        asyncio.run(self.start_server())
        
    def stop(self):
        if self.server:
            self.server.close()


