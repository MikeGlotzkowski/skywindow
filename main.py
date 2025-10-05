"""
NYC Live Aircraft Tracker using OpenSky Network API

Displays real-time aircraft flying above and around NYC location,
filtered for northeast view direction.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from utils import (
    haversine_distance,
    calculate_bearing,
    meters_to_feet,
    mps_to_kmh,
    is_in_bearing_range
)


class NYCFlightTracker:
    """Main class for tracking aircraft over NYC."""
    
    def __init__(self):
        """Initialize the tracker with configuration."""
        # Load environment variables
        load_dotenv()
        
        # Load configuration from config.json
        self.config = self._load_config()
        
        # Get credentials from environment variables
        self.username = os.getenv('OPENSKY_USERNAME')
        self.password = os.getenv('OPENSKY_PASSWORD')
        
        # Get home coordinates
        self.home_lat = float(os.getenv('HOME_LATITUDE', 
                                        self.config['home_coordinates']['latitude']))
        self.home_lon = float(os.getenv('HOME_LONGITUDE', 
                                        self.config['home_coordinates']['longitude']))
        
        # Get bounding box
        self.bbox = {
            'lat_min': float(os.getenv('BBOX_LAT_MIN', 
                                       self.config['bounding_box']['lat_min'])),
            'lat_max': float(os.getenv('BBOX_LAT_MAX', 
                                       self.config['bounding_box']['lat_max'])),
            'lon_min': float(os.getenv('BBOX_LON_MIN', 
                                       self.config['bounding_box']['lon_min'])),
            'lon_max': float(os.getenv('BBOX_LON_MAX', 
                                       self.config['bounding_box']['lon_max']))
        }
        
        # Get view filter
        self.bearing_min = float(os.getenv('BEARING_MIN', 
                                           self.config['view_filter']['bearing_min']))
        self.bearing_max = float(os.getenv('BEARING_MAX', 
                                           self.config['view_filter']['bearing_max']))
        
        # Get refresh interval
        self.refresh_interval = int(os.getenv('REFRESH_INTERVAL', 
                                              self.config['refresh_interval']))
        
        # API endpoint
        self.api_endpoint = self.config['api_endpoint']
        
        # Console for rich output
        self.console = Console()
    
    def _load_config(self) -> Dict:
        """Load configuration from config.json file."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.console.print("[red]Error: config.json not found![/red]")
            sys.exit(1)
        except json.JSONDecodeError:
            self.console.print("[red]Error: Invalid JSON in config.json![/red]")
            sys.exit(1)
    
    def fetch_opensky_data(self) -> Optional[List]:
        """
        Fetch aircraft data from OpenSky Network API.
        
        Returns:
            List of aircraft state vectors or None on error
        """
        params = {
            'lamin': self.bbox['lat_min'],
            'lamax': self.bbox['lat_max'],
            'lomin': self.bbox['lon_min'],
            'lomax': self.bbox['lon_max']
        }
        
        try:
            # Use authentication if credentials are provided
            auth = None
            if self.username and self.password:
                auth = (self.username, self.password)
            
            response = requests.get(
                self.api_endpoint,
                params=params,
                auth=auth,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            # The 'states' field contains the list of aircraft
            return data.get('states', [])
            
        except requests.exceptions.Timeout:
            self.console.print("[yellow]Warning: API request timed out[/yellow]")
            return None
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Error fetching data: {e}[/red]")
            return None
        except json.JSONDecodeError:
            self.console.print("[red]Error: Invalid JSON response from API[/red]")
            return None
    
    def parse_aircraft_state(self, state: List) -> Optional[Dict]:
        """
        Parse aircraft state vector into a dictionary.
        
        OpenSky state vector format:
        [0] icao24 - ICAO 24-bit address
        [1] callsign - Callsign
        [2] origin_country - Country name
        [3] time_position - Last position update (Unix timestamp)
        [4] last_contact - Last contact (Unix timestamp)
        [5] longitude - Longitude in decimal degrees
        [6] latitude - Latitude in decimal degrees
        [7] baro_altitude - Barometric altitude in meters
        [8] on_ground - Boolean
        [9] velocity - Velocity in m/s
        [10] true_track - True track (heading) in degrees
        [11] vertical_rate - Vertical rate in m/s
        [12] sensors - Sensor IDs
        [13] geo_altitude - Geometric altitude in meters
        [14] squawk - Squawk code
        [15] spi - Special purpose indicator
        [16] position_source - Position source
        
        Returns:
            Dictionary with parsed data or None if missing required fields
        """
        # Check if we have position data
        if state[6] is None or state[5] is None:
            return None
        
        aircraft = {
            'icao24': state[0],
            'callsign': (state[1] or '').strip(),
            'origin_country': state[2],
            'latitude': state[6],
            'longitude': state[5],
            'altitude_m': state[7],
            'altitude_ft': meters_to_feet(state[7]),
            'velocity_mps': state[9],
            'velocity_kmh': mps_to_kmh(state[9]),
            'true_track': state[10],
            'last_contact': state[4]
        }
        
        # Calculate distance and bearing from home
        aircraft['distance_km'] = haversine_distance(
            self.home_lat, self.home_lon,
            aircraft['latitude'], aircraft['longitude']
        )
        
        aircraft['bearing'] = calculate_bearing(
            self.home_lat, self.home_lon,
            aircraft['latitude'], aircraft['longitude']
        )
        
        return aircraft
    
    def filter_northeast_view(self, aircraft_list: List[Dict]) -> List[Dict]:
        """
        Filter aircraft to only show those in northeast view.
        
        Args:
            aircraft_list: List of parsed aircraft dictionaries
        
        Returns:
            Filtered list of aircraft in northeast view, sorted by distance
        """
        filtered = []
        
        for aircraft in aircraft_list:
            if is_in_bearing_range(aircraft['bearing'], 
                                   self.bearing_min, 
                                   self.bearing_max):
                filtered.append(aircraft)
        
        # Sort by distance (nearest first)
        filtered.sort(key=lambda x: x['distance_km'])
        
        return filtered
    
    def create_display_table(self, aircraft_list: List[Dict]) -> Table:
        """
        Create a rich table for displaying aircraft data.
        
        Args:
            aircraft_list: List of filtered aircraft
        
        Returns:
            Rich Table object
        """
        table = Table(title=f"🛫 NYC Aircraft Tracker - Northeast View ({self.bearing_min}° - {self.bearing_max}°)")
        
        table.add_column("Callsign", style="cyan", no_wrap=True)
        table.add_column("Country", style="magenta")
        table.add_column("Altitude (ft)", justify="right", style="green")
        table.add_column("Speed (km/h)", justify="right", style="yellow")
        table.add_column("Heading (°)", justify="right", style="blue")
        table.add_column("Distance (km)", justify="right", style="red")
        
        for aircraft in aircraft_list:
            callsign = aircraft['callsign'] or aircraft['icao24']
            country = aircraft['origin_country']
            altitude = f"{aircraft['altitude_ft']:.0f}" if aircraft['altitude_ft'] else "N/A"
            speed = f"{aircraft['velocity_kmh']:.1f}" if aircraft['velocity_kmh'] else "N/A"
            heading = f"{aircraft['true_track']:.0f}" if aircraft['true_track'] else "N/A"
            distance = f"{aircraft['distance_km']:.2f}"
            
            table.add_row(callsign, country, altitude, speed, heading, distance)
        
        return table
    
    def run(self):
        """Main loop for the flight tracker."""
        self.console.print(Panel.fit(
            "[bold green]NYC Live Aircraft Tracker[/bold green]\n"
            f"Home: ({self.home_lat:.6f}, {self.home_lon:.6f})\n"
            f"View: Northeast ({self.bearing_min}° - {self.bearing_max}°)\n"
            f"Refresh: Every {self.refresh_interval} seconds\n"
            "[dim]Press Ctrl+C to exit[/dim]",
            title="🛫 Flight Tracker",
            border_style="blue"
        ))
        
        try:
            while True:
                # Fetch data
                states = self.fetch_opensky_data()
                
                if states is None:
                    self.console.print("[yellow]No data available, retrying...[/yellow]")
                    time.sleep(self.refresh_interval)
                    continue
                
                # Parse aircraft states
                aircraft_list = []
                for state in states:
                    aircraft = self.parse_aircraft_state(state)
                    if aircraft:
                        aircraft_list.append(aircraft)
                
                # Filter for northeast view
                filtered_aircraft = self.filter_northeast_view(aircraft_list)
                
                # Display results
                self.console.clear()
                
                # Show timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.console.print(f"\n[bold]Last Update:[/bold] {timestamp}\n")
                
                if filtered_aircraft:
                    table = self.create_display_table(filtered_aircraft)
                    self.console.print(table)
                    self.console.print(f"\n[green]Found {len(filtered_aircraft)} aircraft in northeast view[/green]")
                else:
                    self.console.print("[yellow]No aircraft found in northeast view[/yellow]")
                
                self.console.print(f"\n[dim]Total aircraft in area: {len(aircraft_list)}[/dim]")
                self.console.print(f"[dim]Next update in {self.refresh_interval} seconds...[/dim]")
                
                # Wait for next refresh
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            self.console.print("\n\n[bold red]Stopping tracker...[/bold red]")
            sys.exit(0)


def main():
    """Entry point for the application."""
    tracker = NYCFlightTracker()
    tracker.run()


if __name__ == "__main__":
    main()
