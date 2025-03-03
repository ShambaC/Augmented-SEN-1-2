from AuthClient import getOAuth
from utils.calcCoords import getCoords
from tqdm import tqdm
from io import TextIOWrapper
from requests_oauthlib import OAuth2Session

import pandas as pd

SEN2_COLLECTION_ID = 'byoc-5460de54-082e-473a-b6ea-d5cbe3c17cca'

def saveImage(oauth: OAuth2Session, long: float, lat: float, idx: int, log_file: TextIOWrapper) -> tuple[str] :
    INITIAL_LONGITUDE = long
    INITIAL_LATITUDE = lat

    coords_data = getCoords(INITIAL_LONGITUDE, INITIAL_LATITUDE)

    # Earth engine format
    # Coords are in (longitude, latitude) format
    boxCoords = coords_data[0]

    ########################################################################
    #                       IMAGE PROPERTIES                               #
    ########################################################################

    img_height = 2500
    img_width = 2500

    bbox = coords_data[1]

    evalScript = """
    //VERSION=3
    function setup() {
        return {
            input: ["B02", "B03", "B04"],
            output: { bands: 3 }
        };
    }

    function evaluatePixel(sample) {
        return [2.5 * sample.B04/10000, 2.5 * sample.B03/10000, 2.5 * sample.B02/10000];
    }

    """

    ########################################################################
    #                    LOCATION AND SEASON DATA                          #
    ########################################################################

    import pandas as pd
    from pathlib import Path

    season = "winter"
    folder = "147"
    fromDateTime = "2023-11-29T23:59:59Z"
    toDateTime = "2024-01-01T00:00:00Z"
    region = ""

    Path(f"./Images/{season}/s2_{folder}").mkdir(parents=True, exist_ok=True)

    if INITIAL_LATITUDE <= 23.5 and INITIAL_LATITUDE >= -23.5 :
        region = "tropical"
    elif (INITIAL_LATITUDE > 23.5 and INITIAL_LATITUDE < 66.5) or (INITIAL_LATITUDE < -23.5 and INITIAL_LATITUDE > -66.5) :
        region = "temperate"
    else :
        region = "arctic"

    # TODO Implement looping on coords
    fileName = f"Images/{season}/s2_{folder}/{season}_img_{region}_p{idx}.png"

    ########################################################################
    #                              REQUEST                                 #
    ########################################################################

    request = {
        "input": {
            "bounds": {
                "bbox": bbox
            },
            "data": [
                {
                    "dataFilter": {
                        "timerange": {
                            "from": fromDateTime,
                            "to": toDateTime
                        }
                    },
                    "type": SEN2_COLLECTION_ID
                }
            ]
        },
        "output": {
            "width": img_width,
            "height": img_height,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/png"
                    }
                }
            ]
        },
        "evalscript": evalScript
    }

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=request)

    if response.ok :
        log_file.write("Response OK\n")
        with open(fileName, 'wb') as fp :
            fp.write(response.content)

        log_file.write("Done saving file\n\n")
        return (fileName, region, season)
    else :
        log_file.write(f"Response code: {response.status_code}\n")
        log_file.write(f"{response.content}\n\n")
        return ("error", "error", "error")


if __name__ == "__main__" :
    import datetime
    from time import time

    # Iterate through rows and download images
    df = pd.read_csv("CoordsList.txt", header=None, names=['long', 'lat'])

    log_file = open("LOG.txt", 'a')
    log_file.write(f"LOGS FOR: {datetime.datetime.now()}\n")

    oauth, token = getOAuth()

    for idx, row in tqdm(df.iterrows(), total=df.shape[0]) :

        # Refresh token
        if time() > (token["expires_at"] - 20) :
            oauth, token = getOAuth()

        long = row.long
        lat = row.lat

        fileName, region, season = saveImage(oauth, long, lat, idx, log_file)
        
        if fileName.strip().lower() == "error" :
            continue

    log_file.close()