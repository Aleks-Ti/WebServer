import asyncio as asyn
import logging
import socket
from pathlib import Path

import aiofiles

from src.config.logger import config_logging
from src.config.settings import VIEWS_DIR

logger = logging.getLogger(__name__)


async def handle_client(client_socket):
    loop = asyn.get_event_loop()
    try:
        data = await loop.sock_recv(client_socket, 1024)
        request_data = data.decode("utf-8")
        content = await load_page_from_get_request(request_data)
        await loop.sock_sendall(client_socket, content)
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        client_socket.close()


async def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 2000))
    server.listen(100)
    server.setblocking(False)  # Очень важно! Сокет должен быть неблокирующим
    logger.info("server run on port: http://127.0.0.1:2000")

    loop = asyn.get_event_loop()

    try:
        while True:
            client_socket, _ = await loop.sock_accept(server)
            asyn.create_task(handle_client(client_socket))
    except KeyboardInterrupt:
        logger.exception("Server shutdown manually.")
    except Exception as err:
        logger.exception(f"Server error: {err}")
    finally:
        server.close()


async def load_page_from_get_request(request_data):
    HDRS = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
    HDRS_404 = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
    path = request_data.split(" ")[1]
    response = "".encode("utf-8")
    views_dir = Path(VIEWS_DIR, path[1:])
    try:
        if views_dir.is_file():
            async with aiofiles.open(views_dir, "rb") as file:
                response = await file.read()
        else:
            async with aiofiles.open(Path(views_dir, "home.html"), "rb") as file:
                response = await file.read()
        return HDRS.encode("utf-8") + response
    except FileNotFoundError:
        logger.warning("404")
        return (HDRS_404 + "Sorry, bro! No page found.").encode("utf-8")
    except IsADirectoryError as e:
        logger.error(str(e))
        return (HDRS_404 + "Requested resource is a directory.").encode("utf-8")
    except Exception as e:
        logger.error(f"Error accessing file: {e}")
        return (HDRS_404 + "An error occurred.").encode("utf-8")


if __name__ == "__main__":
    config_logging(logging.INFO)
    asyn.run(start_server())
