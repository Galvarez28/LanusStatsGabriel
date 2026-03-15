# LanusStats (With Custom Metrics)

This is a customized version of the Python library `LanusStats`. It includes **brand new** features built specifically for extracting advanced data from Sofascore, such as Goalkeeper Saves, Attempted Passes, Attempted Dribbles, Match Histories, and Head-to-Head match data.

---

## 🚀 How to Run and Install This Program

Since this version has **brand new custom stats** (like Goalkeeper Saves), you need to run it directly from this folder on your computer instead of installing the old version from the internet.

### Step 1: Open Your Terminal
Open PowerShell, Command Prompt, or the Terminal inside VS Code.

### Step 2: Navigate to this folder
You need to tell your terminal to go straight into this `LanusStats` folder.
Run this command:
```bash
cd C:\Users\gabri\.gemini\antigravity\scratch\LanusStats
```

### Step 3: Install the Custom Version
Instead of regular `pip install`, you will install *this exact folder* onto your computer so Python can use the new updates. Run this:
```bash
pip install -e .
```
*(Make sure to include the space and the dot at the end!)*

---

## 🟢 How to Use the Custom Sofascore Metrics

Once installed, you can create a Python file (e.g., `my_script.py`) inside your terminal and write the following code to pull the new data:

### 1. Extracting Goalkeeper Saves and Attempted Passes
This custom feature pulls the exact saves a goalkeeper made, and also calculates their "Attempted Passes" based on their accuracy rate.
```python
import LanusStats as ls  

# 1. Initialize SofaScore
sofascore = ls.SofaScore()

# 2. Get Goalkeeper Stats (Saves will automatically appear!)
df = sofascore.scrape_league_stats(
    league="Argentina Liga Profesional", 
    season="2024", 
    save_csv=False, 
    accumulation="per90", 
    selected_positions=["Goalkeepers"]
)

# 3. Print out the names, saves, and attempted passes!
print(df[['player', 'saves', 'attemptedPasses']].head())
```

### 2. Extracting 'Attempted Dribbles' for other positions
Just like passes, you can get "Attempted Dribbles" for forwards or midfielders!
```python
df_forwards = sofascore.scrape_league_stats(
    league="Premier League", 
    season="23/24", 
    save_csv=False, 
    accumulation="total", 
    selected_positions=["Forwards"]
)

# See attempted dribbles!
print(df_forwards[['player', 'attemptedDribbles']].head())
```

*Note: Metrics like `totalShots`, `shotsOnTarget`, `clearances`, and `keyPasses` (assisted shots) are already included automatically in the `df` dataframe for any position that has them!*

### 3. Getting a Team's Last 5 (or 10) Matches
You can use a Team ID to get their recent form easily:
```python
# Pass the team ID (e.g., River Plate is 3221) and how many matches you want (n=5 or n=10)
last_matches = sofascore.get_team_last_matches(team_id=3221, n=5)

for match in last_matches:
    print(match['slug'])
```

### 4. Getting Head-to-Head (H2H) Match History
Pass the exact link of a match on Sofascore to get the history between the two teams playing:
```python
h2h_matches = sofascore.get_match_h2h("https://www.sofascore.com/arsenal-manchester-united/KR#id:11352532")

print(f"Found {len(h2h_matches)} previous matches between these teams!")
```

---

## 🛠️ Pushing This To Your GitHub

When you are ready to upload this to your own personal GitHub account, open your terminal (in this folder) and run these exact commands:

1. Create a completely empty repository on GitHub.com called `LanusStats`.
2. Link this folder to your new Github:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/LanusStats.git
```
3. Push to your repository:
```bash
git push -u origin main
```
It will ask you to quickly sign in to your GitHub account via your browser, and then the code will be live on your profile!
