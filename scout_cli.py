import argparse
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from LanusStats.sofascore import SofaScore

def main():
    parser = argparse.ArgumentParser(description="Scout a player's stats or Head-to-Head form using Sofascore.")
    
    # Required arguments
    parser.add_argument("player", type=str, help="Name of the player, e.g., 'Lionel Messi'")
    parser.add_argument("--stat", type=str, required=True, 
                        help="The exact SofaScore stat name to track (e.g., 'shots', 'shotsOnTarget', 'accuratePasses', 'saves')")
    
    # Optional arguments
    parser.add_argument("--vs", type=str, dest="vs_team", 
                        help="Optional team name to get Head-to-Head history against, e.g., 'Orlando City'")
    
    args = parser.parse_args()

    print(f"🚀 Initializing Scout CLI...")
    sofa = SofaScore()

    print(f"🔍 Searching for player: '{args.player}'...")
    player_data = sofa.search_player(args.player)
    if not player_data:
        print(f"❌ Error: Could not find player '{args.player}'. Try a different spelling.")
        sys.exit(1)

    player_id = player_data['id']
    player_name = player_data['name']
    print(f"✅ Found Player: {player_name} (ID: {player_id})")

    # Get team data
    team_data = player_data.get('team')
    if not team_data:
        print(f"❌ Error: Player {player_name} does not seem to have a current team.")
        sys.exit(1)

    team_id = team_data['id']
    team_name = team_data['name']
    
    # Get tournament data
    tournament = team_data.get('primaryUniqueTournament') or team_data.get('tournament', {}).get('uniqueTournament')
    if not tournament:
        print(f"❌ Error: Could not detect tournament for {team_name}.")
        sys.exit(1)
        
    tourney_id = tournament['id']
    tourney_name = tournament['name']

    print(f"🏆 Detected Tournament: {tourney_name}")
    print(f"⚽ Getting current season ID...")
    season_id = sofa.get_current_season_id(tourney_id)
    if not season_id:
        print(f"❌ Error: Could not determine current season.")
        sys.exit(1)

    # ---------------------------------------------------------
    # ROUTE 1: H2H Matchups
    # ---------------------------------------------------------
    if args.vs_team:
        print(f"🔍 Searching for opponent team: '{args.vs_team}'...")
        opp_data = sofa.search_team(args.vs_team)
        if not opp_data:
            print(f"❌ Error: Could not find team '{args.vs_team}'.")
            sys.exit(1)
        
        opp_id = opp_data['id']
        opp_name = opp_data['name']
        print(f"✅ Found Opponent: {opp_name} (ID: {opp_id})")
        print(f"📊 Fetching last 5 matches for {player_name} vs {opp_name}...")
        
        h2h_history = sofa.get_player_h2h_history(player_id, team_id, opp_id, n=5)
        
        if not h2h_history:
            print(f"⚠️ No recent H2H matches found for {player_name} vs {opp_name}.")
        else:
            print(f"\n--- H2H Stats: '{args.stat}' ---")
            values = []
            for match in h2h_history:
                stat_val = match['statistics'].get(args.stat, 0)
                values.append(stat_val)
                print(f" • Match: {match['match_slug']} -> {args.stat}: {stat_val}")
            
            avg = sum(values)/len(values)
            print(f"\n📈 H2H Average: {round(avg, 2)} {args.stat} across {len(values)} matches.\n")
            
        sys.exit(0)

    # ---------------------------------------------------------
    # ROUTE 2: General Form (L5, L10, Season Avg)
    # ---------------------------------------------------------
    print(f"📊 Fetching season averages and recent form for {player_name}...")
    
    # 1. Season Averages
    try:
        season_stats = sofa.get_player_season_stats_overall(player_id, tourney_id, season_id)
        season_avg = season_stats.get(args.stat, 0)
    except:
        season_avg = 0

    # 2. Last 10 history
    try:
        history = sofa.get_player_match_history(player_id, tourney_id, season_id, n=10)
        l10_values = [h['statistics'].get(args.stat, 0) for h in history]
    except:
        l10_values = []

    l5_values = l10_values[:5]
    
    l5_avg = sum(l5_values)/len(l5_values) if l5_values else 0
    l10_avg = sum(l10_values)/len(l10_values) if l10_values else 0

    print(f"\n" + "="*40)
    print(f" 📊 SCOUT REPORT: {player_name.upper()} ")
    print(f" 🎯 STAT TRACKED: {args.stat}")
    print("="*40)
    print(f" • Season Average: {round(season_avg, 2)}")
    print(f" • Last 5 Matches Average: {round(l5_avg, 2)}")
    print(f" • Last 10 Matches Average: {round(l10_avg, 2)}")
    print(f" • Last 10 Match Values: {l10_values}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
