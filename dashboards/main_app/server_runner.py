"""Lancement du serveur Dash/Flask en développement ou production (Gunicorn)."""

import os


def run_server(app, server) -> None:
    is_prod = os.getenv("ENV", "dev") == "prod"
    ssl_dir = os.getenv("DOCKER_SSL_EXTERNAL_DIR", "")

    if is_prod:
        import gunicorn.app.base

        class StandaloneApp(gunicorn.app.base.BaseApplication):
            def __init__(self, application, options=None):
                self.options = options or {}
                self.application = application
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            "bind": "0.0.0.0:8050",
            "workers": 2,
            "certfile": os.path.join(ssl_dir, "cert.pem"),
            "keyfile": os.path.join(ssl_dir, "key.pem"),
            # Logs d'accès et d'erreurs vers stdout/stderr
            "accesslog": "-",  # Access log vers stdout
            "errorlog": "-",  # Error log vers stderr
            "loglevel": "info",  # Niveau de log
            # Optionnel : capturer les print() de votre app Flask
            "capture_output": True,
        }
        StandaloneApp(server, options).run()
    else:
        app.run(host="0.0.0.0", debug=True)
