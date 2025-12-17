from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from bot.database import Database
from bot.config import FLASK_PORT, MONETAG_ZONE_ID

app = Flask(__name__, static_folder='../webapp')
CORS(app)

db = Database()

@app.route('/')
def index():
    return "🎬 Movie Nest Bot Server Running!"

# ==================== API ENDPOINTS ====================

@app.route('/api/get_points', methods=['GET'])
def get_points():
    """Get user points"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    points = db.get_points(int(user_id))
    return jsonify({'success': True, 'points': points})

@app.route('/api/add_points', methods=['POST'])
def add_points():
    """Add points to user"""
    data = request.json
    user_id = data.get('user_id')
    points = data.get('points', 15)
    source = data.get('source', 'monetag_ad')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    new_balance = db.add_points(int(user_id), int(points), source)
    
    # Log ad view
    if 'ad' in source.lower():
        db.log_ad_view(int(user_id), source, int(points))
    
    return jsonify({
        'success': True,
        'points_added': points,
        'new_balance': new_balance
    })

@app.route('/api/unlock_content', methods=['POST'])
def unlock_content_api():
    """Unlock content"""
    data = request.json
    user_id = data.get('user_id')
    content_id = data.get('content_id')
    method = data.get('method', 'ads')
    
    result = db.unlock_content(int(user_id), int(content_id), method)
    return jsonify(result)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all bot settings"""
    settings = db.get_all_settings()
    return jsonify(settings)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get bot stats"""
    stats = db.get_stats()
    return jsonify(stats)

# ==================== SERVE WEBAPP FILES ====================

@app.route('/watch_ad.html')
def watch_ad():
    return send_from_directory(app.static_folder, 'watch_ad.html')

@app.route('/admin_dashboard.html')
def admin_dashboard():
    return send_from_directory(app.static_folder, 'admin_dashboard.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', FLASK_PORT))
    print(f"🌐 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
