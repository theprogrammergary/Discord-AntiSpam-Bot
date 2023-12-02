## Discord Imposter Bot 🤖

### About - Scammers join open/free discord servers of popular influencers and often try to imitate said influencer. They DM users of the server pretending to be an influencer and offer fake products/services scamming innocent people. Banning/Moderating of these users would require monitoring 24/7 so this bot was created. It checks all users credentials against moderators. If their credentials match too closely to a moderator then that user is banned or kicked. User credentials are checked when users either join the server or update their credentials. Enjoy and 🖕🏼 you scammers.

![image](image.png)

### 1. Requirements

```bash
- VPS Server (I use linode)
- Discord Server
- Discord Bot (Create in discord dev portal)
```

### 2. Clone Git Repo

```bash
# I clone mine into /Documents on the vps
git clone yadi yada
```

### 3. Create Python .venv

```bash
# Create a virtual environment with Python
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install project dependencies from requirements.txt
pip install -r .setup/requirements.txt
```

### 4. Set Your Specific Discord Bot/Server Credientals

```bash
# Create .env file in .setup and set credntials
Example file is provided to see the correct format.
- BOT_TOKEN: for access
- MOD_ROLE_NAME: the role name for mods to add not allowed names
- MOD_LOG_CHANNEL_NAME: for outputting results
```

### 4. Install Supervisor

```bash
# Install package
sudo apt install supervisor

# Create a Supervisor configuration file for your application
sudo nano /etc/supervisor/conf.d/${botName}.conf
```

### 5. Sample Supervisor .conf

```bash
[program:${botName}]
user=${vpsUsername}
directory=/home/bot_manager/Documents/${botName}
command=/home/bot_manager/Documents/${botName}/.venv/bin/python3.10 /home/bot_manager/Documents/${botName}/src/main.py
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/${botName}/${botName}.err.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
stdout_logfile=/var/log/${botName}/${botName}.out.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

### 6. Create Directories/Output Files for Supervisor

```bash
# Create directories and files for Supervisor output logs
sudo mkdir /var/log/${botName}
sudo touch /var/log/${botName}/${botName}.out.log
sudo touch /var/log/${botName}/${botName}.err.log
```

### 7. Start Bots

```bash
sudo supervisorctl start ${botName}
```

### 8. Check Status

```bash
sudo supervisorctl status all
```
