from multiprocessing import freeze_support
from threading import Thread
from urllib.request import urlopen
from urllib.error import URLError

import time
import webbrowser


HOST = "127.0.0.1"
PORT = 8000

URL = f"http://{HOST}:{PORT}"


def open_browser():
    # Wait until FastAPI is ready
    for _ in range(50):
        try:
            with urlopen(f"{URL}/api/health", timeout=0.5) as response:
                if response.status == 200:
                    webbrowser.open(URL)
                    return

        except (URLError, TimeoutError):
            time.sleep(0.2)

    print("Could not open the dashboard automatically.")


def main():
    import uvicorn
    from app.main import app

    # Open browser once the server starts
    Thread(target=open_browser, daemon=True).start()

    print("Starting System Monitor...")
    print(f"Dashboard: {URL}")

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        loop="asyncio",
        http="h11",
        ws="none",
        reload=False,
        workers=1
    )


if __name__ == "__main__":
    freeze_support()
    main()