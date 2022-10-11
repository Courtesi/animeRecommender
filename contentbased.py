import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

pd.options.mode.chained_assignment = None  # default='warn'

def initializeDF():
    aniDF = pd.read_csv("anime.csv", index_col="MAL_ID")

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


# if __name__ == "__main__":
#     test = initializeDF()
#     x = organizeDF(test)
#     y = findRecommendation(test, x, "Sakura-sou no Pet na Kanojo")
#     print(y)