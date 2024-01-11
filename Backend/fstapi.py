# fastapi_server.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import re
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_apache_log_path():
    # Adjust the path based on your Apache configuration
    return "/var/log/apache2/access.log"

def parse_apache_log(log):
    match = re.match(r'(?P<timestamp>.*?)\s+"(?P<method>\S+)\s+(?P<path>\S+)\s+HTTP/\d\.\d"\s+(?P<status_code>\d+)', log)
    if match:
        log_data = match.groupdict()
        return {
            "timestamp": log_data["timestamp"],
            "method": log_data["method"],
            "path": log_data["path"],
            "status_code": int(log_data["status_code"])
        }
    return None

@app.get("/access-logs/")
async def get_access_logs(start_time: str = None, end_time: str = None):
    try:
        apache_log_path = get_apache_log_path()
        
        with open(apache_log_path, "r") as file:
            logs = file.readlines()

        parsed_logs = [parse_apache_log(log) for log in logs if parse_apache_log(log) is not None]

        if start_time:
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            filtered_logs = [log for log in parsed_logs if start_time <= datetime.strptime(log["timestamp"], "%d/%b/%Y:%H:%M:%S%z")]
        else:
            filtered_logs = parsed_logs

        return JSONResponse(content={"access_logs": filtered_logs})
    except Exception as e:
        print("Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
