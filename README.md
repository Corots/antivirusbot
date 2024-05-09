# How to Start a Bot

## 1. Download the Repository
Download the repository using either the GitHub UI or the command line:
```bash
git clone https://github.com/Corots/antivirusbot.git
```

## 2. Install python libralies.

First, set up a Python virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment and install the required Python libraries:
```bash
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate.bat  # On Windows
pip install -r requirements.txt
```
## 3. Create Configuration File

Create a file named .env inside the /config/ folder and use the following template:
```bash
bot_token = 111111111:FDCSDSDGSDGSDFSDFSDFSDFSDF

db_user = postgres
db_passw = my_db_password
db_host = localhost
db_port = 5432
db_name = antivirusbotdb

max_size_mb = 32

virustotal_api = YOUR_VIRUSTOTAL_API_KEY
```
Replace placeholders with your actual bot token, database connection information, Virustotal API key, and maximum file size your bot will accept. (Remeber, telegram bots acccept 50 mb max)

##  4. Set Up PostgreSQL Database and Alembic Migrations

Create a PostgreSQL database with the name specified in the configuration file:
```bash
  CREATE DATABASE antivirusbotdb;
```
Update the alembic.ini file with your database connection information:
```bash
sqlalchemy.url = postgresql://{db_user}:{db_passw}@{db_host}:{db_port}/{db_name}
```
Apply Alembic migrations to create the table structure:
```bash
alembic upgrade head
```

##  5. Start the Bot

Start the bot using the following command:
```bash
python antivirusbot.py
```

Enjoy!
