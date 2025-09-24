# Example module showing how to extend Forklift
# Modules can add routes, background tasks, whatever chaos you need

from flask import jsonify
from datetime import datetime

def init_module(app):
    """called when module loads into reality"""
    print("Example module awakening from slumber")
    
    # add a custom route
    @app.route('/api/module/example/ping')
    def module_ping():
        return jsonify({
            'message': 'pong from the void',
            'timestamp': datetime.now().isoformat(),
            'module': 'example_module'
        })
    
    # another
    @app.route('/api/module/example/souls/richest')
    def richest_souls():
        """find the fattest souls"""
        import sqlite3
        conn = sqlite3.connect('souls.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT discord_name, balance 
            FROM souls 
            ORDER BY balance DESC 
            LIMIT 5
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'name': row['discord_name'],
                'balance': row['balance']
            })
        
        conn.close()
        return jsonify(results)

def cleanup_module():
    """called when module gets yeeted"""
    print("Example module returning to the shadow realm")
