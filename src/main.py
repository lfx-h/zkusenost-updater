from web.app import API
import os
import uvicorn
import click
from dotenv import load_dotenv
from utils import setup_logger

setup_logger()
load_dotenv(override=True)


@click.group()
def cli():
    pass

@cli.command()
def api():
    """
    Starts the web application.
    """
    api = API()

    uvicorn.run(api.app,
        host=os.getenv("HOST"), 
        port=int(os.getenv("PORT"))
    )