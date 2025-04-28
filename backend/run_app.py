import uvicorn
from app.main import app

# Simple startup file for various hosting platforms
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)