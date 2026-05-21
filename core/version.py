import subprocess
import os

# Version Information
# This should match the Git Tag
VERSION = "1.3.0"
APP_NAME = "Little-Tyrant"
WINDOW_TITLE = "小霸王工具箱 (Little Tyrant Tool)"
FILE_NAME = "Little-Tyrant-Tool"

def get_full_version():
    """Returns the version string, potentially with git commit info if available."""
    try:
        # Try to get more detailed info from git if we are in a git repo
        # This will fail in a frozen/distributed build
        git_version = subprocess.check_output(
            ["git", "describe", "--tags", "--always", "--dirty"],
            stderr=subprocess.STDOUT,
            cwd=os.path.dirname(os.path.dirname(__file__))
        ).decode("utf-8").strip()
        return git_version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return VERSION

def get_display_title():
    """Returns the title for the main window including version."""
    return f"{WINDOW_TITLE} v{VERSION}"
