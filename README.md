# LanusStats (Scout Edition)

Welcome to the customized version of **LanusStats**, optimized for deep Prop Betting Analysis! This repository has been supercharged with **brand new** features built specifically for extracting advanced data from Sofascore, like **Head-to-Head (H2H) matchups**, **Last 5 / Last 10 match rolling averages**, and tracking specific stats (e.g., Goalkeeper Saves, Shots, Accurate Passes, etc.).

We've added a **Scout CLI (Command Line Interface)** tool that makes it incredibly easy to lookup a player's recent form or historical head-to-head stats against a specific team just by typing their name!

---

## 🚀 How to Install and Run

### Running Locally (On Your PC)

1. **Open your Terminal** (PowerShell, Command Prompt, or Terminal inside VS Code).
2. **Navigate into this folder:**
   ```bash
   cd path/to/LanusStats
   ```
3. **Install the customized library** (include the dot at the end!):
   ```bash
   pip install -e .
   ```

### Running in Google Colab (Google Terminal)

If you are using **Google Colab**, you need to install the library and a headless Chrome browser so the scraper can bypass protections:

1. Open a new Google Colab notebook.
2. Run this block to install the required system dependencies:
   ```bash
   !apt-get update
   !apt-get install -y chromium-browser chromium-chromedriver
   ```
3. Clone this repository and install it:
   ```bash
   !git clone https://github.com/Galvarez28/LanusStatsGabriel.git
   %cd LanusStatsGabriel
   !pip install -e .
   ```
4. Now you can run the CLI commands using `!python scout_cli.py ...` (see examples below).

---

## 🔍 In-Depth Tutorial: Using `scout_cli.py`

The new `scout_cli.py` script allows you to magically pull all of a player's relevant stats by just providing their name. No more hunting for Player IDs or Season IDs!

### The Required Parameters

* `player` (Positional): The name of the player you want to search for, in quotes. (e.g., `"Lionel Messi"`)
* `--stat` (Required): The exact exact Sofascore variable name for the stat you want to track.
  * Examples: `shots`, `shotsOnTarget`, `accuratePasses`, `saves`, `keyPasses`, `successfulDribbles`, `fouls`

### Example 1: Getting a Player's Recent Form (L5, L10, Season Avg)

If you just want to know how a player has been performing lately, run the script with their name and the stat you are tracking.

**Command:**
```bash
python scout_cli.py "Lionel Messi" --stat "shots"
```

**What it does:**
1. Searches Sofascore for "Lionel Messi".
2. Automatically detects he plays for Inter Miami CF in the MLS.
3. Automatically finds the current 2024 MLS Season ID.
4. Pulls his **Season Average**, **Last 5 Matches Average**, and **Last 10 Matches Average** for `shots`.

**Example Output:**
```text
🚀 Initializing Scout CLI...
🔍 Searching for player: 'Lionel Messi'...
✅ Found Player: Lionel Messi (ID: 12994)
🏆 Detected Tournament: MLS
⚽ Getting current season ID...
📊 Fetching season averages and recent form for Lionel Messi...

========================================
 📊 SCOUT REPORT: LIONEL MESSI 
 🎯 STAT TRACKED: shots
========================================
 • Season Average: 4.8
 • Last 5 Matches Average: 5.2
 • Last 10 Matches Average: 4.5
 • Last 10 Match Values: [5, 4, 6, 3, 8, 4, 5, 2, 4, 4]
========================================
```

### Example 2: Getting Head-to-Head (H2H) Matchups against a Specific Team

If a player is facing a specific team tonight, you want to know how he performed *against that exact team* in his past 5 matchups. Use the optional `--vs` parameter.

**Command:**
```bash
python scout_cli.py "Kevin De Bruyne" --stat "keyPasses" --vs "Arsenal"
```

**What it does:**
1. Finds Kevin De Bruyne and his team (Manchester City).
2. Finds the opponent "Arsenal".
3. Scans Manchester City's recent match history to locate matches strictly against Arsenal.
4. Pulls De Bruyne's `keyPasses` stats from *only* those specific games.

**Example Output:**
```text
🚀 Initializing Scout CLI...
🔍 Searching for player: 'Kevin De Bruyne'...
✅ Found Player: Kevin De Bruyne (ID: 15383)
🏆 Detected Tournament: Premier League
⚽ Getting current season ID...
🔍 Searching for opponent team: 'Arsenal'...
✅ Found Opponent: Arsenal (ID: 42)
📊 Fetching last 5 matches for Kevin De Bruyne vs Arsenal...

--- H2H Stats: 'keyPasses' ---
 • Match: manchester-city-arsenal -> keyPasses: 3
 • Match: arsenal-manchester-city -> keyPasses: 4
 • Match: manchester-city-arsenal -> keyPasses: 2

📈 H2H Average: 3.0 keyPasses across 3 matches.
```

### Example 3: Goalkeeper Saves

You can track goalkeeper performance just like any other stat! 

**Command:**
```bash
python scout_cli.py "Emiliano Martinez" --stat "saves" --vs "Chelsea"
```

---

## 🛠️ Developer Notes

This wrapper uses `undetected_chromedriver` under the hood to scrape Sofascore without getting blocked. 
- If you run into issues with the browser not closing or `The handle is invalid` errors locally on Windows, ensure your Google Chrome is fully updated, or run the script in Google Colab where the display is explicitly handled for headless scraping. 
- The auto-detection relies on the player's *Current Team* and *Current Primary Tournament*. If a player just transferred and hasn't played a game, it might not find their L10 match history if it's looking in the new league.
