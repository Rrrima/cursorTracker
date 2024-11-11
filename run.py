import json
import pandas as pd
import os
from CursorTracker import ContentAwareCursorTracker

def analyze_interaction_data(filename):
    """Analyze cursor interaction data with UI elements"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Extract app statistics
    app_interactions = {}
    for entry in data:
        if 'active_app' in entry and entry['active_app']:
            app_name = entry['active_app']['app_name']
            app_interactions[app_name] = app_interactions.get(app_name, 0) + 1
    
    # Extract UI element statistics
    element_types = {}
    for entry in data:
        if 'element_info' in entry and entry['element_info']:
            element_type = entry['element_info'].get('AXRole', 'unknown')
            element_types[element_type] = element_types.get(element_type, 0) + 1
    
    stats = {
        'total_events': len(data),
        'app_interactions': app_interactions,
        'element_types': element_types,
        'clicks_per_app': {},
        'text_selections': []
    }
    
    # Analyze clicks per application
    for entry in data:
        if entry.get('event_type') == 'click' and entry.get('active_app'):
            app_name = entry['active_app']['app_name']
            stats['clicks_per_app'][app_name] = stats['clicks_per_app'].get(app_name, 0) + 1
    
    # Collect text selections
    for entry in data:
        if entry.get('element_info') and 'AXSelectedText' in entry['element_info']:
            selection = {
                'text': entry['element_info']['AXSelectedText'],
                'app': entry.get('active_app', {}).get('app_name', 'unknown'),
                'timestamp': entry['timestamp']
            }
            stats['text_selections'].append(selection)
    
    return stats



def main():
    tracker = ContentAwareCursorTracker()
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    try:
        tracker.start_tracking()
    except KeyboardInterrupt:
        # tracker.save_data()
        stats = analyze_interaction_data(tracker.data_filename)
        print("\nInteraction Statistics:")
        print(f"Total Events: {stats['total_events']}")
        
        print("\nApplication Interactions:")
        for app, count in sorted(stats['app_interactions'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {app}: {count}")
        
        print("\nUI Element Types Interacted With:")
        for element, count in sorted(stats['element_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {element}: {count}")
        
        print("\nClicks per Application:")
        for app, count in sorted(stats['clicks_per_app'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {app}: {count}")
        
        if stats['text_selections']:
            print("\nRecent Text Selections:")
            for selection in stats['text_selections'][-5:]:  # Show last 5 selections
                print(f"  App: {selection['app']}")
                print(f"  Text: {selection['text'][:50]}...")
                print()

if __name__ == "__main__":
    main()