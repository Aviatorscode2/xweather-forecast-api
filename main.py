import os
from datetime import datetime
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()
# Load variables from the .env file

CLIENT_ID = os.getenv("XWEATHER_CLIENT_ID")
CLIENT_SECRET = os.getenv("XWEATHER_CLIENT_SECRET")
BASE_URL = "https://data.api.xweather.com"
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

import requests

def get_weather_icon(weather):
    """Map weather text to an emoji."""
    text = weather.lower()
    if "rain" in text:
        return "🌧️"
    elif "cloud" in text:
        return "⛅"
    elif "clear" in text or "sun" in text:
        return "☀️"
    elif "snow" in text:
        return "❄️"
    elif "storm" in text or "thunder" in text:
        return "⛈️"
    else:
        return "🌡️"

def analyze_forecast(periods, location_str):
    """Analyzes forecast data and sends alerts for specific conditions."""
    heat_threshold = 35

    for day in periods:
        max_temp = day.get('maxTempC')
        if max_temp is not None and max_temp > heat_threshold:
            date = datetime.fromisoformat(day['dateTimeISO']).strftime('%A, %b %d')
            
            # Create the subject and body for the email
            alert_subject = f"🔥 Heat Alert for {location_str.title()}"
            alert_body = f"A high temperature of {max_temp}°C is expected on {date}."
            
            # Call the email function
            send_email_alert(alert_subject, alert_body)


import smtplib
from email.message import EmailMessage

# Load new environment variables at the top of your script

def send_email_alert(subject, body):
    """Sends an email alert using Gmail."""
    if not all([SENDER_EMAIL, SENDER_APP_PASSWORD, RECEIVER_EMAIL]):
        print("Email credentials not set in .env file. Skipping email.")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        # Connect to Gmail's secure SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            smtp.send_message(msg)
            print("Email alert sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def get_daily_forecast(location_str):
    """Fetches and formats a 7-day daily forecast for a given location."""
    endpoint = f"/forecasts/{location_str}"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "filter": "daily",
        "limit": 10
    }
    url = BASE_URL + endpoint
    
    try:
        response = requests.get(url, params=params)
        # This will raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 
        
        data = response.json()
        # Navigate through the JSON to get the list of forecast periods
        periods = data.get('response', [{}])[0].get('periods', [])
        
        if not periods:
            return f"❌ Could not find forecast data for {location_str.title()}."

        # Start building the output string
        # Build table rows
        rows = []
        for day in periods:
            date = datetime.fromisoformat(day['dateTimeISO']).strftime('%a, %b %d')
            weather = day['weather']
            icon = get_weather_icon(weather)
            max_temp = day.get('maxTempC', 'N/A')
            min_temp = day.get('minTempC', 'N/A')

            rows.append([date, f"{icon} {weather}", f"{max_temp}°C", f"{min_temp}°C"])

        # Create table
        headers = ["Date", "Condition", "High", "Low"]
        table = tabulate(rows, headers=headers, tablefmt="fancy_grid")

        return periods, f"🌤️ 7-Day Forecast for {location_str.title()}:\n\n{table}" 

    except requests.exceptions.HTTPError as http_err:
        # Specifically handle 404 Not Found errors for invalid locations
        if response.status_code == 404:
            return f"❌ Could not find location: '{location_str}'. Please check the format (e.g., 'city,state,country')."
        return f"❌ HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as e:
        # Handle other network-related errors (e.g., DNS failure, connection refused)
        return f"❌ Error connecting to the API: {e}"
    
if __name__ == "__main__":
    print("Weather Forecast Viewer")
    print("-----------------------")
    user_location = input("Enter a location (e.g., 'new york,ny,us', 'london,uk'): ")
    
    if user_location:
        # We need the raw forecast data to analyze it
        forecast_data, formatted_table = get_daily_forecast(user_location.lower().strip())
        
        # Print the formatted table first
        print(formatted_table)

        # If we got valid forecast data, analyze it for alerts
        if forecast_data:
            alerts = analyze_forecast(forecast_data, user_location)
            if alerts:
                print("\n--- Found Conditions to Act On ---")
                for alert in alerts:
                    print(alert)
    else:
        print("No location entered. Exiting.")
