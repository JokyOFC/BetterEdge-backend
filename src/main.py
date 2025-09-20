"""

Main project file

TODO:
    - Refactor for console utils.

created in 12/08/2025 by Joky

"""

from fastapi import FastAPI
from src.api import (
    routes_allocations,
    routes_assets,
    routes_clients,
    routes_daily_returns,
    routes_tickers
)
import logging
import colorlog
import os
import qrcode
import io
from art import text2art
from colorama import Fore, Style, Back
from contextlib import asynccontextmanager
from starlette.middleware.gzip import GZipMiddleware
from src.db.database import engine
from src.config import settings


LOG_FORMAT = "%(log_color)s%(asctime)s | %(levelname)s | %(message)s%(reset)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}

color_formatter = colorlog.ColoredFormatter(
    LOG_FORMAT, datefmt=DATE_FORMAT, log_colors=LOG_COLORS
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)

logger = logging.getLogger("betteredge")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

for log_name in ["uvicorn", "uvicorn.access", "sqlalchemy.engine", "sqlalchemy.pool"]:
    log = logging.getLogger(log_name)
    log.setLevel(logging.INFO)
    log.handlers.clear() 
    log.addHandler(console_handler)

logger = logging.getLogger("betteredge") 

link_docs_qrcode = "http://localhost:8000/docs"

qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )

qr.add_data(link_docs_qrcode)
qr.make(fit=True)
qr_ascii_io = io.StringIO()
qr.print_ascii(out=qr_ascii_io, invert=False)  # invert=True deixa preto no branco
qr_ascii_str = qr_ascii_io.getvalue()

ascii_art = text2art("Better Edge \n Investing", font="random-medium")

qr_lines = qr_ascii_str.splitlines()
art_lines = ascii_art.splitlines()

max_lines = max(len(qr_lines), len(art_lines))
qr_lines += [" " * len(qr_lines[0])] * (max_lines - len(qr_lines))
art_lines += [""] * (max_lines - len(art_lines))

final_lines = [
    qr_lines[i].ljust(len(qr_lines[0]) + 4) + art_lines[i]
    for i in range(max_lines)
]
final_lines_colored = [Fore.CYAN + line + Style.RESET_ALL for line in final_lines]

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not settings.DEBUGGING:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Fore.GREEN + "betteredge_web  | " if os.name != 'nt' else None)
        print("\n".join(final_lines_colored))
        print(Fore.CYAN + "Made with " + Back.CYAN + Fore.BLACK + "FastAPI, Postgres, Redis, Celery, SQLAlchemy, Uvicorn, Alembic and pytest" + Back.BLACK)
        print(" ")
        print(Fore.CYAN + "Running on: http://localhost:8000")
        print(Fore.CYAN + "Docs: " + link_docs_qrcode)
        print(" ")
        print(Fore.CYAN + "- Press \"O\" to open docs")
        print(Fore.CYAN + "- Press \"R\" to Restart application")
        print(" ")
        logger.info(Fore.YELLOW + "🚀 Iniciando aplicação..." + Style.RESET_ALL)

        logger.info(Fore.CYAN + "🔄 Conectando ao banco de dados..." + Style.RESET_ALL)
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: None)
        logger.info(Fore.GREEN + "✅ Banco de dados conectado com sucesso!" + Style.RESET_ALL)

        logger.info(Fore.GREEN + "✅ Aplicação iniciada com sucesso." + Style.RESET_ALL)
        yield

    except Exception as e:
        logger.error(Fore.RED + f"❌ Houve um erro na inicialização da aplicação: {e}" + Style.RESET_ALL)
        raise

    finally:
        logger.info(Fore.MAGENTA + "🔻 Encerrando aplicação..." + Style.RESET_ALL)
        await engine.dispose()
        logger.info(Fore.GREEN + "✅ Conexão com o banco encerrada." + Style.RESET_ALL)

app = FastAPI(title="BetterEdge", version="1.0", description="", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.debug = False

app.include_router(routes_allocations.router, prefix="/alocacoes", tags=["Alocações"])
app.include_router(routes_clients.router, prefix="/clientes", tags=["Clientes"])
app.include_router(routes_assets.router, prefix="/ativos", tags=["Ativos"])
app.include_router(
    routes_daily_returns.router, prefix="/dailyReturns", tags=["Retornos Diários"]
)
app.include_router(routes_tickers.router, prefix="/tickers", tags=["Ticker"])


@app.get("/")
def home():
    return {"status": "ok", "message": "API de investimento pronta!"}
