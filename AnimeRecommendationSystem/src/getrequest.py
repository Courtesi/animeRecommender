import requests
import json
from client_id import CLIENT_ID

def get_request() -> list:
    res = []

    username = input("Enter a username:")

    url = f'https://api.myanimelist.net/v2/users/{username}/animelist?fields=list_status'

    while True:
        response = requests.get(url, headers = {'X-MAL-CLIENT-ID': CLIENT_ID})

        response.raise_for_status()
        anime_list = response.json()
        response.close()

        for entry in anime_list["data"]:
            res.append( (entry["node"]["id"], entry["node"]["title"], entry["list_status"]["score"]) )
        
        if "next" not in anime_list["paging"]:
            break
            
        url = anime_list["paging"]["next"]

    res.sort(key = lambda x: x[2], reverse = True)

    with open("useranimelist.json", "w") as file:
        json.dump(res, file)
    
    return res

# if __name__ == "__main__":
#     get_request()