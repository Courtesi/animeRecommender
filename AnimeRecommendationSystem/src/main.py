import pandas as pd
import statistics as stats
from math import sqrt
import json
from contentbased import organizeDF, initializeDF, findRecommendation
from getrequest import get_request
import warnings
import time
warnings.filterwarnings('ignore')

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

def createRecommendations():
    userAnimeList = get_request()
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
    for entry in userAnimeList:
        if entry[1] in df.columns:
            recommendations = pd.DataFrame(df.nlargest(4,entry[1])['Name'])
            recommendations = recommendations[recommendations['Name']!=entry[1]]
            print("Anime:", entry[1], "\n", recommendations)
        else:
            print("None for", entry[1])
        print("\n")

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
    createRecommendations()

