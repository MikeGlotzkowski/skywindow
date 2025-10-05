"""
Demo script to test the NYC Aircraft Tracker with simulated data.
This allows testing the application without OpenSky API credentials.
"""

import time
from datetime import datetime
from main import NYCFlightTracker
from rich.console import Console
from rich.panel import Panel


def create_mock_aircraft_states():
    """Create mock aircraft state vectors for testing."""
    # Format: [icao24, callsign, origin_country, time_position, last_contact,
    #          longitude, latitude, baro_altitude, on_ground, velocity, true_track,
    #          vertical_rate, sensors, geo_altitude, squawk, spi, position_source]
    
    mock_states = [
        # Aircraft 1: Northeast of Manhattan (bearing ~45°)
        ['abc123', 'UAL456  ', 'United States', 1609459200, 1609459201,
         -73.95, 40.80, 3048, False, 250, 45, 0, None, 3100, None, False, 0],
        
        # Aircraft 2: North-northeast (bearing ~30°)
        ['def456', 'DAL789  ', 'United States', 1609459200, 1609459201,
         -73.985, 40.85, 2440, False, 220, 180, -5, None, 2500, None, False, 0],
        
        # Aircraft 3: East-northeast (bearing ~75°)
        ['ghi789', 'AAL321  ', 'United States', 1609459200, 1609459201,
         -73.85, 40.78, 4572, False, 280, 90, 10, None, 4600, None, False, 0],
        
        # Aircraft 4: Southeast (bearing ~150°, should be filtered out)
        ['jkl012', 'JBU654  ', 'United States', 1609459200, 1609459201,
         -73.90, 40.72, 1524, False, 180, 270, 0, None, 1600, None, False, 0],
        
        # Aircraft 5: East (bearing ~90°, on boundary)
        ['mno345', 'SWA987  ', 'United States', 1609459200, 1609459201,
         -73.80, 40.77, 3658, False, 260, 45, 5, None, 3700, None, False, 0],
        
        # Aircraft 6: North-northeast, closer (bearing ~35°)
        ['pqr678', 'FFT123  ', 'Germany', 1609459200, 1609459201,
         -73.975, 40.80, 5486, False, 300, 120, 0, None, 5500, None, False, 0],
        
        # Aircraft 7: Missing position data (should be filtered out)
        ['stu901', 'BAW456  ', 'United Kingdom', 1609459200, 1609459201,
         None, None, 4000, False, 250, 90, 0, None, 4100, None, False, 0],
    ]
    
    return mock_states


def demo_single_update():
    """Run a single update cycle with mock data."""
    console = Console()
    
    # Create tracker instance
    tracker = NYCFlightTracker()
    
    console.print(Panel.fit(
        "[bold green]NYC Live Aircraft Tracker - DEMO MODE[/bold green]\n"
        f"Home: ({tracker.home_lat:.6f}, {tracker.home_lon:.6f})\n"
        f"View: Northeast ({tracker.bearing_min}° - {tracker.bearing_max}°)\n"
        "[yellow]Using simulated data for demonstration[/yellow]",
        title="🛫 Flight Tracker Demo",
        border_style="blue"
    ))
    
    # Get mock data
    states = create_mock_aircraft_states()
    
    # Parse aircraft states
    aircraft_list = []
    for state in states:
        aircraft = tracker.parse_aircraft_state(state)
        if aircraft:
            aircraft_list.append(aircraft)
    
    # Filter for northeast view
    filtered_aircraft = tracker.filter_northeast_view(aircraft_list)
    
    # Display results
    console.print(f"\n[bold]Demo Timestamp:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if filtered_aircraft:
        table = tracker.create_display_table(filtered_aircraft)
        console.print(table)
        console.print(f"\n[green]Found {len(filtered_aircraft)} aircraft in northeast view[/green]")
    else:
        console.print("[yellow]No aircraft found in northeast view[/yellow]")
    
    console.print(f"\n[dim]Total aircraft in area: {len(aircraft_list)} (1 filtered out for missing position)[/dim]")
    
    # Show bearing details for educational purposes
    console.print("\n[bold]Bearing Details:[/bold]")
    for aircraft in aircraft_list:
        in_view = "✅" if aircraft in filtered_aircraft else "❌"
        callsign = aircraft['callsign'] or aircraft['icao24']
        bearing = aircraft['bearing']
        console.print(f"{in_view} {callsign:10s} - Bearing: {bearing:6.1f}° - Distance: {aircraft['distance_km']:5.2f} km")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NYC AIRCRAFT TRACKER - DEMO MODE")
    print("="*70 + "\n")
    
    demo_single_update()
    
    print("\n" + "="*70)
    print("Demo completed! To use with real data:")
    print("1. Copy .env.example to .env")
    print("2. Add your OpenSky Network credentials to .env")
    print("3. Run: python main.py")
    print("="*70 + "\n")
