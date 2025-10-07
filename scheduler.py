import schedule
import time
from datetime import datetime
# Import the functions from your main script
from main import get_daily_forecast, analyze_forecast

def run_automated_check():
    """
    A dedicated job function that runs the weather check for a 
    predefined location and acts on the data.
    """
    # Hardcode the location for your automated job
    location_to_monitor = "abuja,ng" 
    
    print(f"--- Running daily check for '{location_to_monitor}' at {datetime.now()} ---")
    
    # Get the forecast data and the formatted table
    forecast_data, formatted_table = get_daily_forecast(location_to_monitor)
    
    # You can print the table to a log or save it to a file
    print(formatted_table)

    # If the forecast was fetched successfully, analyze it for alerts
    if forecast_data:
        analyze_forecast(forecast_data, location_to_monitor)
        
    print("--- Daily check complete. ---\n")

# --- Schedule the Job ---
# Schedule the job to run every day at 7:00 AM local time
schedule.every().day.at("01:40").do(run_automated_check)

print("✅ Scheduler started. The script will now run automatically every day at 1:40 AM.")
print("Keep this terminal window open for the scheduler to run.")

# --- Run the Scheduler ---
# This loop continuously checks if a scheduled job is due to run
while True:
    schedule.run_pending()
    time.sleep(1)
