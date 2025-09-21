from fastapi import FastAPI, Request
import json
import time
from src.station_components.station import Station
from src.station_components.statuses_models.models import StationStatus

app = FastAPI()
with open("station_config.json", "r") as f:
    config_dict = json.load(f)

station = Station(config_dict)


@app.middleware("http")
async def measure_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Endpoint {request.url.path} executed in {duration:.3f} seconds")
    return response


@app.get("/")
async def root():
    return {"message": f"Monitoring of Electra station {station.name}"}


@app.get("/station/station_status", response_model=StationStatus)
async def get_station_status():
    return station.get_status()


@app.post("/start_session/")
async def start_session(chargerId, connectorId, powerCapacity):
    charger = station.get_charger(chargerId)
    if not charger:
        return {"message": f"there is no charger with id {chargerId} in the station"}
    if charger.is_session_free(int(connectorId)):
        station.start_session_on_charger(
            chargerId, int(connectorId), int(powerCapacity)
        )
        return {
            "message": f"Session started on charger {chargerId} and connector {connectorId} with power {charger.get_session(int(connectorId)).get_power()}"
        }
    else:
        return {
            "message": f"Session {connectorId} on charger {chargerId} is already active with another vehicle !! "
        }


@app.post("/stop_session/")
async def stop_session(chargerId, connectorId):
    charger = station.get_charger(chargerId)
    if not charger:
        return {"message": f"there is no charger with id {chargerId} in the station"}
    if charger.is_session_free(int(connectorId)):
        return {
            "message": f"Cannot stop session {connectorId} as it is already inactive"
        }

    station.stop_session_on_charger(chargerId, int(connectorId))
    return {"message": f"Session {connectorId} has been removed on charger {chargerId}"}
