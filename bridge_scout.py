import sys
import json
import os
import time

# Ensure LanusStats is in path
sys.path.append(os.path.abspath('LanusStats'))
try:
    from LanusStats.sofascore import SofaScore
except ImportError:
    # If installed via pip -e .
    from LanusStats.sofascore import SofaScore

def scout_player(player_id, league_id, season_id, prop_type):
    sofa = SofaScore()
    
    # 1. Season Averages
    try:
        season_stats = sofa.get_player_season_stats_overall(player_id, league_id, season_id)
        season_avg = season_stats.get(prop_type, 0)
    except:
        season_avg = 0
    
    # 2. Last N history (fetching L10)
    try:
        history = sofa.get_player_match_history(player_id, league_id, season_id, n=10)
        l10_values = [h['statistics'].get(prop_type, 0) for h in history]
    except:
        l10_values = []
        
    l5_values = l10_values[:5]
    
    l5_avg = sum(l5_values)/len(l5_values) if l5_values else 0
    l10_avg = sum(l10_values)/len(l10_values) if l10_values else 0
    
    result = {
        "player_id": player_id,
        "prop_type": prop_type,
        "season_avg": round(season_avg, 2),
        "l5_avg": round(l5_avg, 2),
        "l10_avg": round(l10_avg, 2),
        "l10_history": l10_values,
        "data_quality": "HIGH" if len(l10_values) >= 10 else "MEDIUM"
    }
    
    if not l10_values and season_avg == 0:
        result["data_quality"] = "LOW"
    
    return result

if __name__ == "__main__":
    # Input format: python bridge_scout.py <player_id> <league_id> <season_id> <prop_category>
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Missing arguments", "data_quality": "LOW"}))
        sys.exit(1)
        
    p_id = sys.argv[1]
    l_id = sys.argv[2]
    s_id = sys.argv[3]
    prop = sys.argv[4]
    
    try:
        report = scout_player(p_id, l_id, s_id, prop)
        # Final JSON output for n8n to capture
        print(json.dumps(report))
    except Exception as e:
        print(json.dumps({"error": str(e), "data_quality": "LOW"}))
