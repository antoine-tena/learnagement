import atexit
import os
import socket
import sys
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def protect_tty() -> None:
    """Rend au terminal ses réglages à la sortie, même si compose les a changés."""
    if os.name == "nt" or not sys.stdin.isatty():
        return
    import termios

    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    atexit.register(lambda: termios.tcsetattr(fd, termios.TCSADRAIN, saved))


def ask(prompt: str, is_secret: bool = False, env_key: str | None = None) -> str:
    """Lit une réponse au clavier, ou dans `env_key` quand il n'y a pas de terminal."""
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    if not sys.stdin.isatty():
        raise RuntimeError(
            f"Entrée interactive impossible (pas de TTY) : définis {env_key or 'la valeur'} "
            "en variable d'environnement."
        )
    return getpass(prompt) if is_secret else input(prompt)


def get_local_ip_and_hostname() -> tuple[str, str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Ne se connecte pas vraiment, juste pour déterminer l'interface sortante
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()

    # Résolution DNS inverse (équivalent nslookup) : si pas de PTR record, hostname = IP
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        hostname = ip

    return ip, hostname


def generate_secret(info: str) -> bytes:
    """Génère une clé dérivée compatible avec NextAuth à partir d'un secret de base."""
    base_secret = os.urandom(32).hex()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # 32 octets pour une clé symétrique
        salt=b"",  # pas de sel ici, mais peut être personnalisé
        info=info.encode("utf-8"),
    )
    return hkdf.derive(base_secret.encode("utf-8"))
