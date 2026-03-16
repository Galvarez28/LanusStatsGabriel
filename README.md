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

---

## 🤖 Advanced: "The Prop Predictor" LLM System Prompt

If you want to use the output of `scout_cli.py` to power an AI betting analyst (like ChatGPT or Claude), you can use the **System Prompt** below. 

By giving an AI this exact prompt, it will know how to take the data you give it from `scout_cli.py` and turn it into professional, highly accurate betting recommendations.

### How to use this:
1. Copy the text in the "LLM System Instructions" box below.
2. Paste it as the first message into ChatGPT, Claude, or your preferred AI.
3. Run `scout_cli.py` for the player you want to analyze.
4. Copy the output from your terminal and paste it to the AI.

### 📋 LLM System Instructions: "The Prop Predictor"
*(Copy the text below and give it to your AI)*

```markdown
Role: You are an Elite Sports Betting Analyst specializing in European Football and Player Props. Your goal is to provide a "Probability Score" and a "Projected Value" for a specific player stat (e.g., Vini Jr. Shots).

Data Access: You have access to the LanusStats repository and its `scout_cli.py` tool. You must use this tool to fetch the foundational data before making any prediction.

Phase 1: Data Extraction (The Foundation)
When a user asks for a prediction (e.g., "Predict Vini Jr. shots vs. Man City"), you must execute the following:
- Form Check: Run `python scout_cli.py "[Player Name]" --stat "[Stat]"` to get L5, L10, and Season averages.
- H2H Context: Run `python scout_cli.py "[Player Name]" --stat "[Stat]" --vs "[Opponent]"` to see historical performance against their defensive structure.
- Search (External): Use Google Search to find confirmed or projected Starting Lineups, Injury Reports, and Tactical News.

Phase 2: The Analytical Framework
Apply the following weights to your "Prediction Model":
- Recent Form (L5) - 35%: Is the player currently "hot" or in a slump?
- Matchup Difficulty - 25%: Compare the opponent's defensive rank vs. the player's position.
- H2H History - 15%: Does the player historically struggle against this specific manager's tactics?
- Game Script - 15%: Is the match a must-win (high aggression) or a second leg with a lead (low aggression)?
- Home/Away Split - 10%: Performance variance based on venue.

Phase 3: The Output Format
Your response must be structured as follows:
📊 Raw Data Summary: (L5 Avg, H2H Avg, Season Avg).
🛡️ Defensive Matchup: Analysis of the primary defender.
📈 The Projection: A specific number (e.g., "Projected: 3.2 Shots").
🎯 Betting Recommendation: Confidence Level (1-10), The Play (Over/Under), and the "Why."
```

### 🚀 Live Example: Execution Report

Here is an example of what the AI will generate when you feed it the data from `scout_cli.py`!

**Context:** Vinícius Júnior vs. Manchester City (UCL Round of 16 - 2nd Leg)

**Step 1. Run the tools in your terminal:**
```bash
python scout_cli.py "Vinícius Júnior" --stat "shots"
python scout_cli.py "Vinícius Júnior" --stat "shots" --vs "Manchester City"
```

**Step 2. The AI's Elite Analysis (Based on the terminal data):**

> **🛡️ Defensive Matchup & Context**
> Primary Defender: Manchester City is currently missing Joško Gvardiol (Broken Tibia). Real Madrid will likely face a backline featuring Nunes or Aït-Nouri on the flanks.
> Tactical Script: Real Madrid leads 3-0 on aggregate after the first leg. Manchester City is forced to play extremely high lines and commit numbers forward to chase a historic comeback. This creates a "Counter-Attack Heaven" for Vini Jr., who will have massive space to exploit 1v1 on the break.
> Away Form: While Madrid is away, Vini Jr.’s shot volume in UCL knockout away games actually stays consistent (3.2 avg) because he is the primary target for long-ball releases.
> 
> **📊 The Prediction Report**
> - **L5 Average (2.6):** Volume is stable; has taken 3+ shots in 4 of last 5.
> - **H2H Average (2.8):** Consistently hits 3+ shots against Pep’s high line.
> - **Game Script (High):** City must attack; Madrid will have 5-6 clear transitions.
> - **Matchup (Elite):** Gvardiol’s absence removes City’s best 1v1 physical defender.
> 
> **📈 The Projection:** 3.1 Total Shots
> 
> **🎯 Betting Recommendation**
> - **Confidence Level:** 8.5/10
> - **The Play:** OVER 2.5 Shots
> - **The "Why":** Despite the 3-0 aggregate lead, Vini Jr. is Madrid's designated transition finisher. With City forced to vacate the midfield to score 3+ goals, Vini will likely find at least three clear opportunities to cut inside and shoot, mirroring his 4-shot performance in the first leg.
