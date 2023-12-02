from getrequest import get_request
from helper_functions import initializeDF, initializeUserDF, organizeDF
from client_id import OPENAI_CLIENT_SECRET

import pandas as pd
import time
import warnings
from openai import OpenAI
import requests
from PIL import Image

warnings.filterwarnings('ignore')
pd.options.mode.chained_assignment = None  # default='warn'
# openai.api_key = OPENAI_CLIENT_SECRET
client = OpenAI()

def generate(text): 
    res = client.images.generate(model="dall-e-3", prompt=text, n=1, size="1024x1024", quality="standard")
    return res["data"][0]["url"]

def open_image(text):
    # calling the custom function "generate"
    # saving the output in "url1"
    url1 = generate(text)
    # using requests library to get the image in bytes
    response = requests.get(url1)
    # using the Image module from PIL library to view the image
    Image.open(response.raw)

def createRecommendations(username):
    userAnimeList = get_request(username)
    if len(userAnimeList) == 0:
        print("Your list is empty! Could not find any recommendations. :(")
        return

    aniDF = initializeDF()
    anime_df_dummies = organizeDF(aniDF)
    userDF = initializeUserDF(aniDF, userAnimeList)
    # averageEpisodes = findAverageEpisodesLength(aniDF, userAnimeList)
    # averageContro = findAverageControversialRating(aniDF, userAnimeList)
    
    start_time = time.time()
    df = pd.read_csv("databases/anime_cosine_sim.csv")
    end_time = time.time()
    print("Time Taken:", end_time - start_time)

    df_list = []
    list_names = []
    for entry in userAnimeList:
        list_names.append(entry[1])
        if entry[1] in df.columns:
            recommendations = pd.DataFrame(df.nlargest(5,entry[1])['Name'])
            recommendations = recommendations[recommendations['Name']!=entry[1]]
            # print("Anime:", entry[1], "\n", recommendations)
            df_list.append(recommendations)
        # else:
        #     print("None for", entry[1])
        # print("\n")
    
    combined_df = pd.concat(df_list)

    movie_counts = combined_df.groupby('Name').size().reset_index(name='Count')

    df_filtered = movie_counts[~movie_counts['Name'].isin(list_names)]

    print(df_filtered)

    # alreadySeenSet = set()
    # #Put all the anime titles in userAnimeList into recommendations set as they are already watched by the user
    # for entry in userAnimeList:
    #     alreadySeenSet.add(entry[1])

    # userDF = userDF.reset_index()
    # outercount = 0
    # recommendationSet = set()
    # for _, row in userDF.iterrows():
    #     if row['Name'] not in aniDF['Name'].unique():
    #         continue
    #     if outercount >= 5:
    #         break

    #     outercount += 1
    #     innercount = 0
    #     testing = findRecommendation(aniDF, anime_df_dummies, row['Name'])
    #     print(f"From {row['Name']}, we recommend:")
    #     for _, recommendation in testing.iterrows():
    #         if innercount >= 3:
    #             break
    #         if recommendation.Score == "Unknown":
    #             continue
    #         if recommendation.Name in alreadySeenSet:
    #             continue

    #         innercount += 1
    #         recommendationSet.add(recommendation.Name)
    #         alreadySeenSet.add(recommendation.Name)
    #         print("     ", recommendation.Name, "with a Score of:", recommendation.Score)
        
    #     print()

    # return recommendationSet
            

if __name__ == "__main__":
#     test = initializeDF()
#     x = organizeDF(test)
#     y = findRecommendation(test, x, "Sakura-sou no Pet na Kanojo")
#     print(y)

    # createRecommendations("ahhlmao")

    open_image("Shingeki no Kyojin Anime Poster")