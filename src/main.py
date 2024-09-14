import logging
import socket
from pathlib import Path

from src.config.logger import config_logging
from src.config.settings import VIEWS_DIR

logger = logging.getLogger(__name__)


def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 2000))  # port от 1025 и выше

        server.listen(4)
        logger.info("server run on port: http://127.0.0.1:2000")
        while True:
            client_socket, address = server.accept()
            print(address)
            data = client_socket.recv(1024).decode("utf-8")
            content = load_page_from_get_request(data)
            client_socket.send(content)
            client_socket.shutdown(socket.SHUT_WR)
            client_socket.shutdown(socket.SHUT_RD)
            client_socket.shutdown(socket.SHUT_RDWR)
    except KeyboardInterrupt:
        server.close()
        logger.exception("Ручная остановка сервера.")
    except Exception as err:
        logger.exception("Error server %s", err)
    finally:
        client_socket.close()


def load_page_from_get_request(request_data):
    HDRS = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
    path = request_data.split(" ")[1]
    response = "".encode("utf-8")
    views_dir = Path(VIEWS_DIR, path[1:])
    try:
        with open(views_dir, "rb") as file:
            response = file.read()
    except FileNotFoundError:
        logger.warning("404")
    return HDRS.encode("utf-8") + response


if __name__ == "__main__":
    config_logging(logging.INFO)
    start_server()
