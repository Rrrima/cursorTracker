import Quartz
from Cocoa import  NSBitmapImageRep, NSBitmapImageFileTypePNG
import Cocoa
import time
import pandas as pd
from pynput import mouse
import json
from datetime import datetime
import AppKit
from AppKit import NSCursor
import os
from PIL import Image, ImageDraw
import io
import numpy as np
from AppTracker import ApplicationTracker
from UIElementTracker import UIElementTracker
from PyQt6.QtWidgets import QApplication
from CursorInfoWidget import CursorInfoWidget
from PyQt6.QtCore import QTimer
import signal 
import sys

class ContentAwareCursorTracker:
    def __init__(self):
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        self.cursor_info_widget = CursorInfoWidget()
        self.cursor_info_widget.show()
        self.cursor_data = []
        self.start_timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        self.start_time = time.time()
        self.ui_tracker = UIElementTracker()
        self.app_tracker = ApplicationTracker()
        self.last_cursor_type = None
        self.last_active_app = None
        self.ss_dir = os.path.join('data', f'screenshots_{self.start_timestamp}')
        self.downsample_factor = 0.05
        self.data_filename = os.path.join('data',f"cursor_data_{self.start_timestamp}.json")
        
        if not os.path.exists(self.ss_dir):
            os.makedirs(self.ss_dir)

        print("Setting up signal handlers...")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)  # Keep Qt responsive to signals
        self.timer.start(200)

    

    def signal_handler(self, _signum, _frame):
        print("\nStop tracking...")  
        try:
            self.listener.stop()
            self.cursor_info_widget.close()
            self.save_data()
            self.app.quit()
        except Exception as e:
            print(f"Error in signal handler: {e}")
        finally:
            sys.exit(0) 
    

    def get_cursor_info(self):
        """Get comprehensive information about cursor position and context"""
        mouse_loc = Quartz.NSEvent.mouseLocation()
        screen = AppKit.NSScreen.mainScreen()

        # Get cursor type
        cursor = NSCursor.currentSystemCursor()
        cursor_type = self._get_cursor_type(cursor)

        # Convert to screen coordinates
        x = mouse_loc.x
        y = screen.frame().size.height - mouse_loc.y
        
        # Get UI element and app information
        element_info = self.ui_tracker.get_element_info(x, y)
        app_info = self.app_tracker.get_active_app_info()

         # Capture screenshot
        screenshot_filename = None
        if self.last_cursor_type != cursor_type or self.last_active_app != app_info.get('app_name'):
            screenshot_filename = self._capture_screenshot(x,y)
            self.last_cursor_type = cursor_type
            self.last_active_app = app_info.get('app_name')
        
        return {
            'timestamp': datetime.now().strftime('%m%d_%H%M%S'),
            'time_elapsed': time.time() - self.start_time,
            'x': x,
            'y': y,
            'cursor_type': cursor_type,
            'screen': self._get_current_screen(),
            'element_info': element_info,
            'active_app': app_info,
            'screenshot': screenshot_filename
        }
    
    def _get_cursor_type(self, cursor):
        """Map NSCursor to readable cursor type"""
        hs_x = cursor.hotSpot().x
        hs_y = cursor.hotSpot().y
        if hs_x == 4 and hs_y == 4:
            return "arrow"
        elif hs_x == 4 and hs_y == 9:
            return "ibeam"
        elif hs_x == 13 and hs_y == 8:
            return "pointing_hand"
        elif hs_x == 9 and hs_y == 9:
            return "resizer"
        elif hs_x == 16 and hs_y == 16:
            return "dragging_hand"
        elif hs_x == 11 and hs_y == 11:
            return "crosshair"
        else:
            return "unknownType: " + str(hs_x) + " " + str(hs_y)
    
    def _get_current_screen(self):
        screens = Cocoa.NSScreen.screens()
        mouse_loc = Quartz.NSEvent.mouseLocation()
        # Find the screen that contains the mouse location
        for i, screen in enumerate(screens):
            frame = screen.frame()
            if (frame.origin.x <= mouse_loc.x <= frame.origin.x + frame.size.width and
                frame.origin.y <= mouse_loc.y <= frame.origin.y + frame.size.height):
                return i
        return 0

    def on_move(self, x, y):
        cursor_info = self.get_cursor_info()
        cursor_info['event_type'] = 'move'
        self.cursor_data.append(cursor_info)
        self.cursor_info_widget.update_info(cursor_info)
        self.app.processEvents()

    def on_click(self, x, y, button, pressed):
        cursor_info = self.get_cursor_info()
        cursor_info['event_type'] = 'click'
        cursor_info['button'] = str(button)
        cursor_info['pressed'] = pressed
        self.cursor_data.append(cursor_info)
        self.cursor_info_widget.update_info(cursor_info)
        self.app.processEvents()
       
    def on_scroll(self, x, y, dx, dy):
        cursor_info = self.get_cursor_info()
        cursor_info['event_type'] = 'scroll'
        cursor_info['dx'] = dx
        cursor_info['dy'] = dy
        self.cursor_data.append(cursor_info)
        self.cursor_info_widget.update_info(cursor_info)
        self.app.processEvents()
       

    def save_data(self):
        with open(self.data_filename, 'w') as f:
            json.dump(self.cursor_data, f, indent=2)

    def start_tracking(self):
        print("Starting content-aware cursor tracking... Press Ctrl+C to stop.")

        # Start mouse listener in a separate thread
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        
        self.listener.start()

        # self.app.exec()
        self.app.exec()
       
        # with mouse.Listener(
        #     on_move=self.on_move,
        #     on_click=self.on_click,
        #     on_scroll=self.on_scroll) as listener:
        #     listener.join()

        # try:
        #     # Start Qt event loop in main thread
        #     self.app.exec()
        # except KeyboardInterrupt:
        #     print("\nStopping tracker...")

    def _capture_screenshot(self,x,y):
        """Capture and save the current screen"""
        try:
            # Get the current window
            window = Quartz.CGWindowListCreateImage(
                Quartz.CGRectInfinite,
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID,
                Quartz.kCGWindowImageDefault
            )
            
            # Convert to NSBitmapImageRep
            bitmap = NSBitmapImageRep.alloc()
            bitmap.initWithCGImage_(window)
            
            # Convert to PNG data
            png_data = bitmap.representationUsingType_properties_(
                NSBitmapImageFileTypePNG, 
                None
            )

            # Convert to PIL Image
            image = Image.open(io.BytesIO(png_data))

            # Calculate new size
            new_size = tuple(int(dim * self.downsample_factor) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Draw cursor position
            draw = ImageDraw.Draw(image)
            cursor_x = int(x * self.downsample_factor)
            cursor_y = int(y * self.downsample_factor)
            draw.ellipse((cursor_x-10, cursor_y-10, cursor_x+10, cursor_y+10), outline="red", width=5)
            
            # Save to file with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.ss_dir,f"screenshot_{timestamp}.png")
            image.save(filename)
            # print(f"Screenshot saved to {filename}")
            
            return filename
        
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

