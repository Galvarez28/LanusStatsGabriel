from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Ensure the library is accessible
sys.path.append(os.path.abspath('.'))
from LanusStats.sofascore import SofaScore

app = Flask(__name__)
CORS(app) # Allow n8n to talk to this API
sofa = SofaScore()

@app.route('/scout', methods=['POST'])
def scout():
    data = request.json
    p_id = data.get('player_id')
    l_id = data.get('league_id')
    s_id = data.get('season_id')
    prop = data.get('prop_type', 'saves')
    
    try:
        # 1. Get Season Summary
        season_stats = sofa.get_player_season_stats_overall(p_id, l_id, s_id)
        season_avg = season_stats.get(prop, 0)
        
        # 2. Get L10 history
        history = sofa.get_player_match_history(p_id, l_id, s_id, n=10)
        l10_values = [h['statistics'].get(prop, 0) for h in history if 'statistics' in h]
        
        l5_values = l10_values[:5]
        l5_avg = sum(l5_values)/len(l5_values) if l5_values else 0
        l10_avg = sum(l10_values)/len(l10_values) if l10_values else 0
        
        return jsonify({
            "status": "success",
            "season_avg": round(season_avg, 2),
            "l5_avg": round(l5_avg, 2),
            "l10_avg": round(l10_avg, 2),
            "l10_history": l10_values,
            "data_quality": "HIGH" if len(l10_values) >= 10 else "MEDIUM"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "data_quality": "LOW"}), 500

if __name__ == '__main__':
    print("🚀 Scout Betting API is starting on http://localhost:5000")
    print("Wait for the browser to initialize...")
    app.run(port=5000)
