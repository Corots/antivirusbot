from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config.config_reader import config


#Connect engine to session
engine = create_engine(f"postgresql://{config.db_user}:{config.db_passw}@{config.db_host}:{config.db_port}/{config.db_name}", echo=False)
session = Session(engine, future = True)
