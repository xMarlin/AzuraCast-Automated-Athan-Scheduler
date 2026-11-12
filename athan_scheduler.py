#!/usr/bin/env python3
import requests
import datetime
import urllib3
import sys

# Disable SSL warnings for self-signed AzuraCast certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURATION - EDIT THESE VALUES
# ==========================================
AZURACAST_URL = "https://YOUR_AZURACAST_IP_OR_DOMAIN/api"
API_KEY = "YOUR_API_KEY_HERE" 
STATION_ID = 1  # Usually 1, check your URL
PLAYLIST_ID = 5 # The ID of the Athan Interrupt playlist

CITY = "Cairo"
COUNTRY = "Egypt"
METHOD = 5  # Calculation method (5 = Egyptian General Authority)
# ==========================================

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def time_to_minutes(time_str):
    """Converts HH:MM to minutes since midnight for AzuraCast API"""
    h, m = map(int, time_str.split(':'))
    return (h * 60) + m

def get_prayer_times():
    # Force the timezone to Cairo (or your local timezone) to ensure correct dates
    try:
        from zoneinfo import ZoneInfo
        today = datetime.datetime.now(ZoneInfo("Africa/Cairo")).strftime("%d-%m-%Y")
    except ImportError:
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        
    url = f"http://api.aladhan.com/v1/timingsByCity/{today}?city={CITY}&country={COUNTRY}&method={METHOD}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch prayer times. Status: {response.status_code}")
        sys.exit(1)
        
    data = response.json()
    timings = data['data']['timings']
    
    # Only extract the 5 daily prayers
    prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    return {p: timings[p].split(' ')[0] for p in prayers}

def update_azuracast_schedule(prayer_times):
    playlist_url = f"{AZURACAST_URL}/station/{STATION_ID}/playlist/{PLAYLIST_ID}"
    
    # 1. Fetch current playlist details
    res = requests.get(playlist_url, headers=headers, verify=False)
    if res.status_code != 200:
        print(f"Failed to fetch playlist. Check your API Key and Playlist ID. Status: {res.status_code}")
        sys.exit(1)
        
    playlist_data = res.json()

    # 2. Build the new schedule items array
    new_schedules = []
    for prayer, clean_time in prayer_times.items():
        start_min = time_to_minutes(clean_time)
        
        new_schedules.append({
            "start_time": start_min,
            "end_time": start_min + 1, # 1 minute duration
            "start_date": None,
            "end_date": None,
            "days": [1, 2, 3, 4, 5, 6, 7], # Every day
            "loop_once": True
        })
        print(f"Prepared schedule for {prayer} at {clean_time}")

    # 3. We must send ONLY the allowed fields to avoid 500 errors
    payload = {
        "schedule_items": new_schedules,
        "name": playlist_data.get('name', 'Athan Interrupt'),
        "type": "general", # Crucial: Must be General Rotation
        "source": playlist_data.get('source', 'songs'),
        "order": playlist_data.get('order', 'shuffle'),
        "is_enabled": True,
        "weight": 10, # Crucial: High weight to override music
        "backend_options": ["interrupt", "single_track"],
        "is_jingle": playlist_data.get('is_jingle', True)
    }
    
    # 4. Push the update
    update_res = requests.put(playlist_url, headers=headers, json=payload, verify=False)
    
    if update_res.status_code == 200:
        print("✅ Successfully updated AzuraCast schedule!")
    else:
        print(f"❌ Failed to update: {update_res.status_code}")
        print(update_res.text)

if __name__ == "__main__":
    print("Fetching prayer times...")
    times = get_prayer_times()
    print(f"Times found: {times}")
    print("Updating AzuraCast...")
    update_azuracast_schedule(times)
    print("Done!")
