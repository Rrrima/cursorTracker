from Cocoa import NSWorkspace

class ApplicationTracker:
    def get_active_app_info(self):
        """Get information about the currently active application"""
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.activeApplication()
        
        if active_app:
            return {
                'app_name': active_app['NSApplicationName'],
                'bundle_id': active_app.get('NSApplicationBundleIdentifier', 'Unknown'),
                'process_id': active_app['NSApplicationProcessIdentifier']
            }
        return None