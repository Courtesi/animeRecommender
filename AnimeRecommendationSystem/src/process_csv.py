import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import time

def separate_genres_and_types_into_anime_cosine_sim_csv():
    df = pd.read_csv('databases/anime.csv')
    # df2 = df.drop(columns = ["Members", "Score-10", "Score-9", "Score-8", "Score-7", "Score-6", "Score-5", "Score-4",\
    # "Score-3", "Score-2", "Score-1"])

    # genres_series = df['Genres']

    # genres_list = genres_series.str.split(',').explode()

    # unique_genres = genres_list.unique()
    # unique_genres = list(unique_genres)
    # unique_genres.sort()

    sample_size = 7500
    df = df.sample(n=sample_size, replace=False, random_state=490)

    df = df.reset_index()
    df = df.drop('index',axis=1)

    mlb_genres = MultiLabelBinarizer()
    genre_matrix = mlb_genres.fit_transform(df['Genres'])

    mlb_type = MultiLabelBinarizer()
    type_matrix = mlb_type.fit_transform(df['Type'].apply(lambda x: [x]))

    feature_matrix = pd.DataFrame(np.concatenate([genre_matrix, type_matrix], axis=1),
                              columns=list(mlb_genres.classes_) + list(mlb_type.classes_))

    cosine_sim = cosine_similarity(feature_matrix)

    rounded_cosine_sim = np.round(cosine_sim, decimals=3)

    df = pd.DataFrame(rounded_cosine_sim, columns=df['Name'], index=df['Name']).reset_index()

    df.to_csv("databases/anime_cosine_sim.csv", index=False)

    return df

if __name__ == "__main__":
    start_time = time.time()

    # df = separate_genres_and_types_into_anime_cosine_sim_csv()
    df = pd.read_csv("databases/anime_cosine_sim.csv")

    end_time = time.time()

    time_elapsed = end_time - start_time
    print(time_elapsed)
    print(df.head())