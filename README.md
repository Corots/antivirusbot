How to start a bot:

1. Download a repo. Use github UI or the command
   git clone https://github.com/Corots/antivirusbot.git

2. Install python libralies.

Install python virtual enviroment first, by

python -m venv venv

After connecting to virtual enviroment, install python libralies

pip install -r requirements.txt

3. Create file.env into /config/ folder. Use this template

bot_token = 111111111:FDCSDSDGSDGSDFSDFSDFSDFSDF

db_user = postgres
db_passw = my_db_password
db_host = localhost
db_port = 5432
db_name = antivirusbotdb

max_size_mb = 32

virustotal_api = YOUR_VIRUSTOTAL_API_KEY

Where bot_token - is your telegram bot token, db\*\* is your database connection info, and virustotal_api is your api key from virustotal.com, max_size_mb - maximum size of the file your bot will accept (telegram bots acccept 50 mb max)

4. Create postgresql database with a db_name, connect database to alembic, and use alembic migrations to create a table structure.

- To create a database, use sql command :
  CREATE DATABASE antivirusbotdb

- To connect database to alembic:

Go into alembic.ini and find a
sqlalchemy.url = postgresql://{db_user}:{db_passw}@{db_host}:{db_port}/{db_name}

Replace it with your own data

- Use alembic to upload a table structure on your database
  alembic upgrade head

5. Start a bot using "python antivirusbot.py" command

Enjoy
