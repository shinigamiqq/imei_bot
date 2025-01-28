from fastapi import APIRouter, HTTPException
import requests
import json


router = APIRouter()


@router.get("/api/check-imei/imei={imei}&token={token}")
async def check_imei(imei: int, token: str):
    url = 'https://api.imeicheck.net/v1/checks'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    body = json.dumps({
        "deviceId": imei,
        "serviceId": 12
    })

    response = requests.get(url=url, headers=headers, data=body)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=404, detail="IMEI not found or invalid token")

