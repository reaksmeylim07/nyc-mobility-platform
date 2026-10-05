import os
import platform
import sys
from datetime import datetime, timezone


def main() -> None:
    # Read a setting from the environment; use "local" if it isn't set
    env = os.getenv("PIPELINE_ENV", "local")

    print("NYC Mobility Platform — ingestion service")
    print(f"Time (UTC):       {datetime.now(timezone.utc).isoformat()}")
    print(f"Environment:      {env}")
    print(f"Python version:   {sys.version.split()[0]}")
    print(f"Operating system: {platform.system()} {platform.machine()}")
    print(f"Working Directory: {os.getcwd()}")


if __name__ == "__main__":
    main()