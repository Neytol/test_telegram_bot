import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),  # Логи в файл
        logging.StreamHandler(sys.stdout)  # И в консоль
    ]
)
logger = logging.getLogger(__name__)
