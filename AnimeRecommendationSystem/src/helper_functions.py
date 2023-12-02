import pandas as pd
from sklearn.neighbors import NearestNeighbors
import statistics as stats
import json
import numpy as np
from math import sqrt

def initializeDF():
    aniDF = pd.read_csv("databases/anime.csv", index_col="MAL_ID")

    return aniDF

def organizeDF(aniDF):
    # Drop the animes with null values
    df_NONULL = aniDF[aniDF.Genres.notna() & aniDF.Type.notna()]

    df_NOUNKNOWNGENRES = df_NONULL[df_NONULL.Genres != "Unknown"]

    anime_df_dummies = df_NOUNKNOWNGENRES[df_NOUNKNOWNGENRES.Type != "Unknown"]

    genres = anime_df_dummies.Genres.str.split(", ", expand=True)

    unique_genres = pd.Series(genres.values.ravel('A')).dropna().unique()

    genre_dummies = pd.get_dummies(genres)

    for genre in unique_genres:
        input = genre_dummies.loc[:, genre_dummies.columns.str.endswith(genre)]
        anime_df_dummies.loc["Genre: " + genre] = input.sum(axis=1)
        
    type_dummies = pd.get_dummies(anime_df_dummies.Type, prefix="Type:", prefix_sep=" ")

    anime_df_dummies = pd.concat([anime_df_dummies, type_dummies], axis=1)

    anime_df_dummies = anime_df_dummies.drop(columns=["Name", "Score", "Genres", "Type", "Episodes", \
        "Ranked", "Popularity", "Members","Score-10", "Score-9", "Score-8", "Score-7", "Score-6", \
        "Score-5", "Score-4", "Score-3", "Score-2", "Score-1"])
    
    return anime_df_dummies


def findRecommendation(aniDF, anime_df_dummies, name):
    # Helper function to get the features of an anime given its name
    def helper(official_name):
        test = aniDF[aniDF.Name == official_name].index
        return anime_df_dummies.loc[test]

    # Build and "train" the model
    neigh = NearestNeighbors(n_neighbors=11, algorithm='auto')
    neigh.fit(anime_df_dummies)

    # Get the features of this anime
    item = helper(name)

    # Get the indices of the most similar items found
    # Note: these are ignoring the dataframe indices and starting from 0
    indexArray = neigh.kneighbors(item, return_distance=False)

    newIndexArray = np.array(indexArray)
    # Show the details of the items found
    return aniDF.loc[aniDF.index[newIndexArray][0]]

def findAverageEpisodesLength(aniDF, userAnimeList):
    episodesList = []
    searchAniDF = aniDF.loc[:, 'Episodes']
    for entry in userAnimeList:
        try:
            episodeNumber = searchAniDF.loc[entry[0]]
            x = int(episodeNumber)
            episodesList.append(x)
        
        except:
            pass
    mode = stats.mode(episodesList)
    return {"Mode": mode, "Count": episodesList.count(mode)}

def findAverageControversialRating(aniDF, userAnimeList):
    controversialRatingList = []
    searchAniDF = aniDF.loc[:, ['Score-10', 'Score-9', 'Score-8', 'Score-7', 'Score-6', 'Score-5', 'Score-4', 'Score-3', 'Score-2', 'Score-1']]

    for entry in userAnimeList:
        try:
            ScoreList = searchAniDF.loc[entry[0]]
            rating_10_1 = 0.2 * findConfidence(int(ScoreList.loc["Score-10"]), int(ScoreList.loc["Score-1"]))
            rating_9_2 = 0.2 * findConfidence(int(ScoreList.loc["Score-9"]), int(ScoreList.loc["Score-2"]))
            rating_8_3 = 0.2 * findConfidence(int(ScoreList.loc["Score-8"]), int(ScoreList.loc["Score-3"]))
            rating_7_4 = 0.2 * findConfidence(int(ScoreList.loc["Score-7"]), int(ScoreList.loc["Score-4"]))
            rating_6_5 = 0.2 * findConfidence(int(ScoreList.loc["Score-6"]), int(ScoreList.loc["Score-5"]))
            totalRating = rating_10_1 + rating_9_2 + rating_8_3 + rating_7_4 + rating_6_5
            totalRating = int(totalRating * 1000) / 1000.0
            controversialRatingList.append(totalRating)
        except:
            pass

    return int(stats.mean(controversialRatingList) * 1000) / 1000.0

def initializeUserDF(aniDF, userAnimeList):
    nameList = []
    x = ""
    for entry in userAnimeList:
        nameList.append(entry[1])

    userAnimeDFList = [["Name", "Score", "Genres", "Type", "Episodes", "Ranked", "Popularity",\
    "Members", "Score-10", "Score-9", "Score-8", "Score-7", "Score-6", "Score-5", "Score-4",\
    "Score-3", "Score-2", "Score-1"]]

    for entry in userAnimeList:
        try:
            if entry[1] in aniDF.values:
                x = aniDF.loc[aniDF['Name'] == entry[1]].values.tolist()
                userAnimeDFList.append(x[0])
        except:
            print("Something's wrong. :(")

    userDF = pd.DataFrame(userAnimeDFList[1:], columns = userAnimeDFList[0])
    userDF = userDF.drop(columns = ["Members", "Score-10", "Score-9", "Score-8", "Score-7", "Score-6", "Score-5", "Score-4",\
    "Score-3", "Score-2", "Score-1"])
    userDF = userDF[userDF.Episodes != "Unknown"]
    userDF = userDF[userDF.Score != "Unknown"]

    with open("userAnimeDF.json", "w") as file:
        json.dump(userDF.values.tolist(), file)
    return userDF

#Found from Reddit Open Source Code
def findConfidence(ups, downs):
    
    n = ups + downs

    if n == 0:
        return 0

    z = 1.281551565545
    p = float(ups) / n

    left = p + 1/(2*n)*z*z
    right = z*sqrt(p*(1-p)/n + z*z/(4*n*n))
    under = 1+1/n*z*z

    return (left - right) / under
