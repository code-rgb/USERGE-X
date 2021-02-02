import uvicorn
import os

from web import webX

Port = int(os.environ.get('PORT', 8080))


if __name__ == "__main__":
    uvicorn.run("web:webX", host="0.0.0.0", port=Port, reload=True, access_log=True, log_level="info")

