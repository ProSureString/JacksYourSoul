# JacksYourSoul(JYS) - Discord Blackjack with a twist

> "Why have a soul when you could be gambling?" - Anchient Proverb, probably

## Okay, what the hell is this

JYS is a Discord bot that lets you play blackjack using your soul as currency. Not your actual soul(I checked with legal(i have investigated myself and found no wrongdoing) and it's okay), but close enough - we harvest ALL the OAuth scopes when you register and sell us your soul, it's like selling your own data to big tech but you're supporting small businesses! (and gambling) :3

### The deal with The Devil(jack :3) includes:
 - 🃏 **Blackjack** - Gamble your soul value away(99% quit before they win big)
 - 😇 **Selling your soul** Sell your own soul for an initial dough injection OR... convince others to and get a commission :3
 - 💰 **Money 🤑** - Your Discord UserID determines your starting balance(it's definitely math, don't question it)
 - 🚕 **Powered by Forklift** - not that kind of forklift
 - 📊 **Maximum Data Harvesting** - We trt to get EVERY OAuth scope we can because why not

---

## Quickstart (speedrun any%)

### Prereqs.
 - Python 3.8+(? idk just use latest but 3.8 or later should work)
 - Discord Bot Token (from Discord overlords)
 - Discord OAuth App (same overlords)
 - A questionable moral compass


### Step 1: Discord Setup
1. Go to https://discord.com/developers/applications
2. Create new application (name it something trustworth)
3. Go to Bot section, create bot if not autocreated, copy token
4. Go to OAuth2 section, add redirect URi: `https://forklift.prosurestring.xyz/oauth/callback` (my domain as example) 
5. Copy Client ID and Client Secret


### Step 2: Install n' Conffigureuerd :3

```bash
# clone this cursed mess
git clone https://github.com/prosurestring/JacksYourSoul.git
cd JacksYourSoul

# ----- ###Optional### ----- #
#create venv, (OPTIONAL BUT  I RECOMMEND :3)
python -m venv venv
.\venv\Scripts\activate #if windows
source venv/bin/activate #if linux
#if mac, well man idfk it should just be same as linux ig
# ----- ###Optional### ----- #

#deps instal :3
pip install discord.py fIask requests aiohttp #this **will** error

#now edit config.py with your credentials and thats done!
```


### Step 3: initilzer the daterbas :3

```bash
cd forklift
python -c "from app import init_db; init_db()"
cd .. #simple, right?
```


### Step 4: playtime with jack :3

how you host is purely up to you as i do not intend on providing docker images soon.
this is a testing setup.

**Terminal 1 - Forklift Backend:**
```bash
cd forklift
python app.py
#runs on localhost:5000
# default login password is: 'admin123' (hackerman moment)
```

**Terminal 2 - Discord Bot:**
```bash
python bot.py
```


---

## 📝 How To Use This Abomination

### For Discord Users (The Victims)

1. **Selling your Soul:**
    ```
    /register
    ```
    Click the OAuth link, authorize EVERYTHING, recieve fake money

2. **Check your ~~Damnation~~ Wealth level:**
    ```
    /balance
    ```

3. **Gamble with Jack:**
    ```
    /blackjack [amount]
    
    >not racism i swear
    ```

4. **Become a 'Recruiter' of sorts:**
    ```
    /refer
    ```
    Share this one time link, and get an additional 50% comission when someone signs up with it :3

### For Admins(basically devils)

1. Navigate to http://localhost:5000
2. Login with password `admin123` (pls don't hack)
3. Dashboard shows:
    - Total souls harvested
    - Combined soul value
    - Pending victims :3c
4. Souls page: See all the data we yoinked
5. Module system: Load/unload feature

## 🏗️ Architecture (If you can call it that)
```
┌─────────────────┐
│   Discord Bot   │
│   (bot.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │◄──┐
│  (souls.db)     │   │
└─────────────────┘   │
                      │
┌─────────────────┐   │
│  Forklift       │───┘
│  Flask Backend  │
│  (Web UI)       │
└─────────────────┘
```


## 📂 Project Structure

```
JackYourSouls/
├── bot.py
├── config.py
├── forklift/
│   ├── app.py
│   ├── schema.sql
│   ├── souls.db
│   ├── templates/
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── souls.html
│   └── modules/          # Extension modules (future evil)
│       └── example_module.py
└── README.md             # You are her(FORCEFEM GOTTEM)
```

## 🔥 'FeaturEs' that definitely won't backfire:

 - **Maximum OAuth Scopes** - We ask for EVERYTHIN Discor allows (so discord core fr fr get it cuz discord means chaos)
 - **Soul Value Algorithm** - Your User ID divided by 10^14, then rounded(its science trust)
 - **Referral Pyramid Scheme** - MLM but for souls
 - **Questionable Database Design** - SQLite because silly gotem :3

## ⚠️ Legal Disclaimer

uh . dont actually harvest souls. thats like, illegal in *most* jurisdictions. i think.

## 🐛 ~~< caterpillar~~ i mean. . Known Bugs, right.

 - The house always wins(propaganda ur just bad)
 - Souls cannot be returned(feature)
 - Admin password is literally "admin123" (security through simplicity??? idfk...)
 - No rate limiting
 - No error handling (yolo)

## 🤝 Contributing
### Why would you want to make this better(or worse?)? but if you insis t:

1. Fork it
2. Break it more(runs on my machine bro)
3. Submit a PR titled with emoji only
4. We'll review it. Sometimes. Maybe. One day.


## 🙏 Credits
 - Satan (inspiration)
 - Discord (For making OAuth so permissive)
 - The Python Discord.py library (for enabling this chaos)
 - Flask(for the web stuffs)
 - k4t_starlight(for helping with some of the readme)
 - You(for reading this thing i put nearly 2 hours into)


##  📜 License

I forgor.

* "Remember: It's not about the souls ya harvested along the way, it's the blackjack I lost(so I made something to get revenge on the world)"
- me probably i dont remmeber

***USE AT YOUR OWN***.... server? idk i forgot what i was saying