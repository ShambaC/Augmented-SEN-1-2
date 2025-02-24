from AuthClient import SessionData

oauth, token = SessionData

IW_COLLECTION_ID = 'byoc-3c662330-108b-4378-8899-525fd5a225cb'

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

request = {
    "input": {
        "bounds": {
            "bbox": [
                88.4410829646665,
                22.567793946666132,
                88.32709981036963,
                22.769912393094224
            ]
        },
        "data": [
            {
                "dataFilter": {
                    "timerange": {
                        "from": "2024-11-29T23:59:59Z",
                        "to": "2024-12-01T00:00:00Z"
                    }
                },
                "type": IW_COLLECTION_ID
            }
        ]
    },
    "output": {
        "width": 1400,
        "height": 2500,
        "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/jpeg"
                }
            }
        ]
    },
    "evalscript": evalScript
}

url = "https://sh.dataspace.copernicus.eu/api/v1/process"
response = oauth.post(url, json=request)

if response.ok :
    print("Response OK")
    with open("testImages/TestImageRes2.jpeg", 'wb') as fp :
        fp.write(response.content)
        print("Done saving file")
else :
    print(f"Response code: {response.status_code}")
    print(response.content)