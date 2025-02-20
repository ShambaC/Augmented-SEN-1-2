from AuthClient import SessionData

oauth, token = SessionData

res = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
print(f"Response: {res.content}")