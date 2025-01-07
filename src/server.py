# main.py
import datetime
import uvicorn
from fastapi import FastAPI, Response
import requests
from generate_clash_config import build_config, load_yaml_str, dump_yaml_str

app = FastAPI()


@app.get("/")
async def read_root(url: str, convert: str = ""):
    ct = datetime.datetime.now()
    url = url + f"?_={ct.timestamp()}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        yaml_data = load_yaml_str(response.text)
        data = build_config(yaml_data, convert=convert)
        data = dump_yaml_str(data)
        return Response(data, media_type="text/yaml")

        return data.encode("utf8")
    return {"Hello": f"{url}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
