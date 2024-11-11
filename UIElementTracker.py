from ApplicationServices import AXUIElementCreateSystemWide, AXUIElementCopyElementAtPosition, AXUIElementCopyAttributeValue
import AppKit


class UIElementTracker:
    def __init__(self):
        self.system_wide_element = AXUIElementCreateSystemWide()
        
    def get_element_info(self, x, y):
        """Get information about UI element at given coordinates"""
        element = self._get_element_at_position(x, y)

        if not element:
            return None
            
        info = {}
        try:
        # Get basic properties
            for attribute in [
                "AXRole",
                "AXRoleDescription",
                "AXTitle",
                "AXDescription",
                "AXHelp",
                "AXSelectedText",
                "AXFocused"
            ]:
                try:
                    status, value = AXUIElementCopyAttributeValue(element, attribute, None)
                    # print(error)
                    if status == 0:
                        info[attribute] = str(value)
                except Exception:
                    continue
                
            # Get parent element for context
            status, parent = AXUIElementCopyAttributeValue(element, "AXParent", None)
            if status == 0:
                pr_status, parent_role = AXUIElementCopyAttributeValue(parent, "AXRole", None)
                pt_status, parent_title = AXUIElementCopyAttributeValue(parent, "AXTitle", None)
                if pr_status == 0:
                    info["parent_role"] = str(parent_role)
                if pt_status == 0:
                    info["parent_title"] = str(parent_title)
                
        except Exception as e:
            print(f"Error getting element info: {e}")

        return info
    
    def _get_element_at_position(self, x, y):
        """Get UI element at specific coordinates"""
        try:
            element = None
            # Convert screen coordinates to CG coordinates
            screen = AppKit.NSScreen.mainScreen()
            height = screen.frame().size.height
            y = height - y  # Flip y coordinate
            status, element = AXUIElementCopyElementAtPosition(self.system_wide_element, x, y, None)
            return element
        
        except Exception as e:
            print(f"Error getting element at position: {e}")
            return None
        