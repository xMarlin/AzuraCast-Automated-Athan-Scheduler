# 🕌 AzuraCast Automated Athan Scheduler

This repository contains a Python script and setup guide to automatically fetch daily Islamic prayer times for a specific city and update an [AzuraCast](https://www.azuracast.com/) playlist.

Because prayer times change slightly every day, AzuraCast's built-in scheduler cannot handle them natively. This script uses a nightly `cron` job to fetch the exact times for tomorrow and update AzuraCast via its API, ensuring the Athan interrupts the radio stream at the exact correct minute, every single day.

---

## 🛠️ Prerequisites

1. A self-hosted AzuraCast instance.
2. Server SSH access (Linux).
3. Python 3 installed on the server.

---

## 🚀 Setup Instructions

### Step 1: AzuraCast Web Interface Configuration

Before running the script, you must prepare AzuraCast to accept the Athan.

1. **Upload Audio:** Upload your Athan audio file to the AzuraCast **Media** library.
2. **Create Playlist:** Go to **Playlists** and click **Create New Playlist**. Name it `Athan Interrupt`.
3. **Basic Info Settings:**
   * **Playlist Type:** Set to **General Rotation**.
     > ⚠️ **Crucial:** Do not use "Advanced" or it will ignore the schedule.
   * **Playlist Weight:** Set to **10**.
     > ⚠️ **Crucial:** This ensures the Athan overrides your standard music playlists.
   * **Allow Requests:** **Uncheck** this (you don't want listeners triggering the Athan).
4. **Add Content:** Add your Athan MP3 file to this playlist.
5. **Advanced Settings:** Go to the **Advanced** tab of the playlist and check:
   * ✅ Interrupt other songs to play at scheduled time
   * ✅ Only play one track at scheduled time
6. **Dummy Schedule:** Go to the **Schedule** tab. Add a random dummy schedule (e.g., 12:00 PM every day). The script will overwrite this automatically.
7. **Note the Playlist ID:** Look at your browser URL while editing the playlist.
   Example: `https://your-ip/station/1/playlists/5` → the Playlist ID is `5`.
8. **Generate API Key:** Click your profile icon in the top right → **API Keys** → **Create API Key**. Give it full permissions and copy the key.

---

### Step 2: Server Installation

SSH into your server and run the following commands.

**1. Install Python dependencies:**

```bash
sudo apt update
sudo apt install python3-requests -y
```

**2. Create the script file:**

```bash
sudo nano /usr/local/bin/athan_scheduler.py
```

**3. Add the script:**

Either download `athan_scheduler.py` from this repo, or copy the script provided in this repo and paste it directly into the nano editor you just opened.

Then save and exit:
* Press `Ctrl + O`, then `Enter` to save.
* Press `Ctrl + X` to exit.

**4. Make the script executable:**

```bash
sudo chmod +x /usr/local/bin/athan_scheduler.py
```

---

### Step 3: Test the Script

Run the script manually to ensure it works:

```bash
python3 /usr/local/bin/athan_scheduler.py
```

If successful, it should output:

```
✅ Successfully updated AzuraCast schedule!
```

You will then see the 5 exact prayer times in your AzuraCast playlist's **Schedule** tab.

---

### Step 4: Automate with Cron

Set the script to run every night at 12:05 AM to fetch the next day's times.

**1. Open the crontab editor:**

```bash
sudo crontab -e
```

*(If prompted to select an editor, choose `nano` - usually option 1.)*

**2. Add this line to the very bottom of the file:**

```bash
5 0 * * * /usr/bin/python3 /usr/local/bin/athan_scheduler.py >> /var/log/athan.log 2>&1
```

This tells the server: *at 00:05 (12:05 AM) every day, run the Python script, and save any output and errors to a log file.*

**3. Save and exit:**
* Press `Ctrl + O`, then `Enter` to save.
* Press `Ctrl + X` to exit.

---

## 🔍 Troubleshooting

Check the log file to see the result of the last run:

```bash
cat /var/log/athan.log
```
