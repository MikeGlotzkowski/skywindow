# 🛫 NYC Live Aircraft Tracker

A real-time aircraft tracking application that displays flights above and around NYC using the OpenSky Network API. The tracker filters aircraft based on your viewing direction and displays them in a live-updating terminal dashboard.

## ✨ Features

- **Real-time Aircraft Tracking**: Fetches live flight data from OpenSky Network API
- **Directional Filtering**: Shows only aircraft in your field of view (northeast by default)
- **Rich Terminal Display**: Beautiful console interface with color-coded information
- **Distance Calculation**: Shows how far each aircraft is from your location
- **Live Updates**: Automatically refreshes every 10 seconds (configurable)
- **Comprehensive Data**: Displays callsign, country, altitude, speed, heading, and distance

## 📋 Requirements

- Python 3.7 or higher
- OpenSky Network API account (optional but recommended for better rate limits)

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MikeGlotzkowski/skywindow.git
   cd skywindow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your settings**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenSky Network credentials:
   ```
   OPENSKY_USERNAME=your_username_here
   OPENSKY_PASSWORD=your_password_here
   ```
   
   You can also customize other settings in `.env`:
   - `HOME_LATITUDE` and `HOME_LONGITUDE` - Your location coordinates
   - `BEARING_MIN` and `BEARING_MAX` - Your viewing direction (30-120° is northeast)
   - `REFRESH_INTERVAL` - How often to update (in seconds)
   - Bounding box coordinates for the area to monitor

4. **Verify your setup** (optional):
   ```bash
   python quickstart.py
   ```
   
   This will check your dependencies and configuration.

## 🎮 Usage

### Quick Start

Check your setup and get started quickly:
```bash
python quickstart.py
```

### Run the Tracker

Run the live tracker with real data:
```bash
python main.py
```

### Demo Mode

Try the demo with simulated data (no API credentials needed):
```bash
python demo.py
```

The application will:
1. Connect to the OpenSky Network API
2. Fetch aircraft data within the NYC bounding box
3. Filter for aircraft in your northeast view (30° to 120° bearing)
4. Display a live-updating table with flight information
5. Refresh every 10 seconds (or your configured interval)

Press `Ctrl+C` to exit the application.

## 📊 Display Format

The tracker displays the following information for each aircraft:

| Column | Description |
|--------|-------------|
| **Callsign** | Aircraft callsign or ICAO 24-bit address |
| **Country** | Origin country of the aircraft |
| **Altitude (ft)** | Current altitude in feet |
| **Speed (km/h)** | Current ground speed in kilometers per hour |
| **Heading (°)** | True track (heading) in degrees |
| **Distance (km)** | Distance from your location in kilometers |

Aircraft are sorted by distance, with the nearest aircraft shown first.

## ⚙️ Configuration

### Configuration Files

The application uses two configuration methods:

1. **`.env` file** (recommended): For sensitive credentials and user-specific settings
2. **`config.json`**: For default configuration values

### Adjusting Your View Direction

By default, the tracker is configured for a northeast view (30° to 120° bearing). To adjust this:

- **North**: 0° or 360°
- **East**: 90°
- **South**: 180°
- **West**: 270°

For example, to track aircraft in the **east-southeast** direction (90° to 150°):
```env
BEARING_MIN=90
BEARING_MAX=150
```

### Bounding Box

The bounding box defines the geographic area to query. The default covers the NYC metro area:

```env
BBOX_LAT_MIN=40.7
BBOX_LAT_MAX=40.9
BBOX_LON_MIN=-74.1
BBOX_LON_MAX=-73.8
```

To cover a larger area (including JFK, LGA, EWR airports), you can expand these values.

### Refresh Rate

Adjust how often the tracker updates:

```env
REFRESH_INTERVAL=10  # seconds
```

**Note**: OpenSky Network has rate limits. For anonymous users, the limit is quite restrictive. With authentication, you get better limits. Don't set the refresh interval too low to avoid hitting rate limits.

## 🔧 API Information

### OpenSky Network API

The application uses the OpenSky Network API to fetch real-time aircraft data:
- **Endpoint**: `https://opensky-network.org/api/states/all`
- **Documentation**: https://openskynetwork.github.io/opensky-api/

### Rate Limits

- **Anonymous users**: 10 requests per 10 seconds
- **Authenticated users**: 100 requests per 10 seconds
- **Contributors**: Higher limits (contact OpenSky Network)

It's recommended to create a free account at https://opensky-network.org/ for better rate limits.

## 🐛 Troubleshooting

### No data showing

1. **Check your internet connection**
2. **Verify API credentials** in your `.env` file
3. **Check rate limits**: You may be hitting OpenSky's rate limit
4. **Adjust bounding box**: Make sure it covers a valid area with air traffic
5. **Try different times**: There may be no aircraft in your view at the moment

### API Timeout Errors

- The application has a 10-second timeout for API requests
- If you see timeout warnings, your internet connection may be slow
- The tracker will automatically retry on the next refresh

### No aircraft in northeast view

- Aircraft may not be present in your specific viewing direction
- Try expanding the bearing range (e.g., 0° to 180° for entire north hemisphere)
- Check the "Total aircraft in area" count - if it's 0, there are no aircraft in the bounding box

## 🎯 Use Cases

- **Aviation Enthusiasts**: Track flights you see from your window
- **Learning Tool**: Understand air traffic patterns in your area
- **Photography**: Know when interesting aircraft are approaching
- **Education**: Learn about flight paths and aircraft operations

## 📝 Project Structure

```
skywindow/
├── main.py              # Main application entry point
├── utils.py             # Utility functions (distance, bearing, conversions)
├── demo.py              # Demo mode with simulated data
├── quickstart.py        # Setup verification and quick start guide
├── config.json          # Default configuration
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available for personal use.

## 🙏 Acknowledgments

- **OpenSky Network**: For providing free access to real-time flight data
- **Rich**: For the beautiful terminal UI library

## 🔗 Links

- OpenSky Network: https://opensky-network.org/
- OpenSky API Documentation: https://openskynetwork.github.io/opensky-api/

---

**Note**: This is a personal hobby project for tracking aircraft visible from your location. Please respect OpenSky Network's terms of service and rate limits.
