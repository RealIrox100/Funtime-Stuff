
import base64
import github3
import json
import time
from datetime import datetime, timezone


GITHUB_USER = "RealIrox100"
REPOSITORY = "Funtime-Stuff"
APP_ID = "abc"


def github_connect():
    """Connect to the application's GitHub repository."""
    with open("secret.txt", encoding="utf-8") as f:
        token = f.read().strip()

    session = github3.login(token=token)
    repo = session.repository(GITHUB_USER, REPOSITORY)

    if repo is None:
        raise RuntimeError("Repository not found or access denied.")

    return repo


def get_json(repo, path):
    """Retrieve a JSON file as data, never executable code."""
    remote_file = repo.file_contents(path)

    if remote_file is None:
        raise FileNotFoundError(path)

    content = base64.b64decode(remote_file.content)
    return json.loads(content.decode("utf-8"))


def save_json(repo, path, data):
    """Upload a JSON file to the repository."""
    content = json.dumps(data, indent=2).encode("utf-8")

    repo.create_file(
        path=path,
        message=f"Save application data: {path}",
        content=content
    )


class GitHubApp:
    def __init__(self, app_id):
        self.id = app_id
        self.repo = github_connect()

    def get_config(self):
        """Read application settings from GitHub."""
        return get_json(
            self.repo,
            f"config/{self.id}.json"
        )

    def get_status(self):
        """Generate a predefined local status report."""
        return {
            "app_id": self.id,
            "status": "running",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    def save_status(self):
        """Upload the local application's status."""
        status = self.get_status()

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%dT%H%M%SZ")

        path = f"data/{self.id}/{timestamp}.json"

        save_json(self.repo, path, status)
        print(f"Status uploaded: {path}")

    def run(self):
        """Periodically read settings and upload status."""
        while True:
            try:
                config = self.get_config()

                if config.get("upload_status", False):
                    self.save_status()

                interval = config.get(
                    "interval_seconds", 3600
                )

                if type(interval) is not int:
                    raise ValueError("Invalid interval")

                interval = max(60, min(interval, 86400))

            except Exception as error:
                print(f"Application error: {error}")
                interval = 3600

            time.sleep(interval)


if __name__ == "__main__":
    app = GitHubApp(APP_ID)
    app.run()

