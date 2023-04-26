import pandas as pd
from sklearn.metrics.pairwise import sigmoid_kernel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient
from decouple import config
import certifi


def fetchDB():
    client_uri = config('mongo_uri')
    print(client_uri)

    client = MongoClient(client_uri, tlsCAFile=certifi.where())
    print('connected to cluster')

    db = client['music_list']
    col = db['songtitles']

    df = pd.DataFrame(list(col.find()))
    print(df.head())

    return df

def getSongTitle():
    #return song title from elasticsearch search
    pass


def updateRecPlaylist(df, feature_cols, recPlaylist, song_title):
    '''Returns 20 song playlist updated with 3 recommended songs added based on searched song title and 3 random songs removed'''
    n = 20
    scaler = MinMaxScaler()
    normalized_df =scaler.fit_transform(df[feature_cols])
    
    indices = pd.Series(df.index, index=df['song_title']).drop_duplicates()
    
    #Cosine similarity and sigmoid kernel matrices based on input matrix
    cosine = cosine_similarity(normalized_df)
    sig_kernel = sigmoid_kernel(normalized_df)

    recPlaylist = generate_recommendation(df, song_title, n, sig_kernel, indices)

    return recPlaylist


def generate_recommendation(df, song_title, n, model_type, indices):
    '''Returns top n songs based on similarity score to input song'''
    index=indices[song_title]
    score=list(enumerate(model_type[indices['Parallel Lines']]))
    similarity_score = sorted(score,key = lambda x:x[1],reverse = True)
    similarity_score = similarity_score[1:n]
    top_songs_index = [i[0] for i in similarity_score]
    top_songs=df['song_title'].iloc[top_songs_index]

    return list(top_songs)


def main():
    df = fetchDB()

    feature_cols=['acousticness', 'danceability', 'duration_ms', 'energy',
                  'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
                  'speechiness', 'tempo', 'time_signature', 'valence']
    
    searchedSong = getSongTitle()
    print(f'\nSearched song: {searchedSong}\n\n')

    recPlaylist = updateRecPlaylist(df, feature_cols, recPlaylist, searchedSong)
    print(f'Playlist of similar songs:\n{recPlaylist}\n\n')


main()




# Dockerize
