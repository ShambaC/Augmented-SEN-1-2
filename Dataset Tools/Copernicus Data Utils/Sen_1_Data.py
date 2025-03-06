from AuthClient import getOAuth
from utils.calcCoords import getCoords
from tqdm import tqdm
from io import TextIOWrapper
from requests_oauthlib import OAuth2Session

import pandas as pd

IW_COLLECTION_ID = 'byoc-3c662330-108b-4378-8899-525fd5a225cb'

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
            input: ["VV"],
            output: { bands: 1 }
        };
    }

    function evaluatePixel(sample) {
        return [sample.VV];
    }

    """

    ########################################################################
    #                    LOCATION AND SEASON DATA                          #
    ########################################################################

    import pandas as pd
    from pathlib import Path

    season = "winter"
    folder = "172"
    fromDateTime = "2023-11-29T23:59:59Z"
    toDateTime = "2024-01-01T00:00:00Z"
    region = ""

    Path(f"./Images/{season}/s1_{folder}").mkdir(parents=True, exist_ok=True)

    if INITIAL_LATITUDE <= 23.5 and INITIAL_LATITUDE >= -23.5 :
        region = "tropical"
    elif (INITIAL_LATITUDE > 23.5 and INITIAL_LATITUDE < 66.5) or (INITIAL_LATITUDE < -23.5 and INITIAL_LATITUDE > -66.5) :
        region = "temperate"
    else :
        region = "arctic"

    # TODO Implement looping on coords
    fileName = f"Images/{season}/s1_{folder}/{season}_img_{region}_p{idx}.png"

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
                    "type": IW_COLLECTION_ID
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
        return (f"{season}/s1_{folder}/{season}_img_{region}_p{idx}.png", f"{season}/s2_{folder}/{season}_img_{region}_p{idx}.png", region, season)
    else :
        log_file.write(f"Response code: {response.status_code}\n")
        log_file.write(f"{response.content}\n\n")
        return ("error", "error", "error", "error")


if __name__ == "__main__" :
    import datetime
    from time import time

    # Iterate through rows and download images
    df = pd.read_csv("CoordsList.txt", header=None, names=['long', 'lat'])
    prompt_list = []

    log_file = open("LOG.txt", 'a')
    log_file.write(f"LOGS FOR: {datetime.datetime.now()}\n")

    oauth, token = getOAuth()

    for idx, row in tqdm(df.iterrows(), total=df.shape[0]) :

        # Refresh token
        if time() > (token["expires_at"] - 20) :
            oauth, token = getOAuth()

        long = row.long
        lat = row.lat

        s1_fileName, s2_fileName, region, season = saveImage(oauth, long, lat, idx, log_file)
        
        if s1_fileName.strip().lower() == "error" :
            continue

        prompt_list.append([s1_fileName, s2_fileName, f"Season: {season}, Region: {region}"])

    prompt_df = pd.DataFrame(prompt_list, columns=['s1_fileName', 's2_fileName', 'prompt'])
    prompt_df.to_csv("Images/prompts_172.csv", index=False)
    log_file.close()