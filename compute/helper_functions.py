from collections import defaultdict
import pandas as pd

def get_bpm_range(bpm_diff):
    if bpm_diff < 10:
        return 0.6
    elif bpm_diff < 20:
        return 0.4
    elif bpm_diff < 30:
        return 0.3
    elif bpm_diff < 40:
        return 0.1
    else:
        return 0.0

def get_loudness_range(loudness_diff):
    if loudness_diff < 2:
        return 0.4
    elif loudness_diff < 15:
        return 0.3
    elif loudness_diff < 35:
        return 0.2
    elif loudness_diff < 40:
        return 0.1
    else:
        return 0.0
    
def calculate_danceability(loudness_series, bpm_series):
    loudness_series = (loudness_series + 7).abs()
    bpm_series = (bpm_series - 120).abs()
    loudness_score = loudness_series.apply(get_loudness_range)
    bpm_score = bpm_series.apply(get_bpm_range)
    danceability = bpm_score + loudness_score
    return danceability

#check year var is used to tell the function that it should keep the year and make a decade column, otherwise it will check that the title is not empty
def prune_data(df, check_year):
    # Remove rows with missing values
    df = df.dropna()
    # Remove rows with invalid values
    if(not check_year):
        df = df[(df['title'] != '')]
    df = df[(df['year'] > 0) & (df['year'] < 2024)]
    df = df[(df['bpm'] > 0) & (df['bpm'] < 300)]
    df = df[(df['loudness'] > -100) & (df['loudness'] < 0)]
    return df

def year_to_decade(year):
    return year - year % 10


#check_year var is used to tell the function that it should keep the year and make a decade column, otherwise it will focus on the title
def preprocess_data(df, check_year):
    # Calculate danceability
    new_df = prune_data(df, check_year)
    new_df['danceability'] = calculate_danceability(new_df['loudness'], new_df['bpm'])
    # Prune the data
    if(check_year):
        new_df = new_df.drop(['title'], axis=1)
    new_df['decade'] = new_df['year'].apply(year_to_decade)
    new_df = new_df.drop(['loudness', 'bpm', 'year'], axis=1)
    return new_df


def get_title_words(title):
    #remove all of the words in parentheses
    count = title.count("(")
    if(count):
        for _ in range(count):
            start_index = title.find("(")
            end_index = title.find(")")
            if end_index == -1:
                return []
            title = title[:start_index] + title[end_index+1:]
    # remove special characters
    title = title.translate(str.maketrans('', '', '\'’!?.:;,'))
    title = title.lower()
    split_words = title.split()
    split_words = [word for word in split_words if len(word) > 2]
    return split_words

def words_by_danceability(words, danceability, decade):
    word_count = []
    for word in words:
        word_count.append((word, danceability, decade))
    return word_count

def danceability_by_word(df):
    word_count = []
    for index, row in df.iterrows():
        words = get_title_words(row['title'])
        word_count.extend(words_by_danceability(words, row['danceability'], row['decade']))
    return word_count


def get_word_count_store_by_decade(word_count):
    word_store_by_decade = defaultdict(list) # dictionary to store the danceability of each word by decade as key
    for word, danceability, decade in word_count:
        if decade in word_store_by_decade:
            if word in word_store_by_decade[decade]:
                word_store_by_decade[decade][word].append(danceability)
            else:
                word_store_by_decade[decade][word] = [danceability]
        else:
            word_store_by_decade[decade] = {word: [danceability]}
    return word_store_by_decade


def get_word_count_ind_and_by_decade(word_store_by_decade):
    df_count_by_decade = pd.DataFrame(columns=['word', 'danceability', 'decade', 'count']) #dataframe to store the mean danceability of each word by decade
    df_count_by_word = pd.DataFrame(columns=['word', 'danceability', 'count'])
    individual_word_store = defaultdict(list)# dictionary to store the danceability of each word 
    for decade in word_store_by_decade:
        for word in word_store_by_decade[decade]:
            #calculting the mean danceability of word in decade
            average = sum(word_store_by_decade[decade][word]) / len(word_store_by_decade[decade][word])
            rounded_average = round(average, 2) 
            # add the word, danceability, decade and count to the df_count_by_decade dataframe
            df_count_by_decade.loc[len(df_count_by_decade.index)] = [word, rounded_average, decade, len(word_store_by_decade[decade][word])]

            # add it to the individual_word_store dictionary as well
            if word in individual_word_store:
                individual_word_store[word].extend(word_store_by_decade[decade][word])
            else:
                individual_word_store[word] = word_store_by_decade[decade][word]
    for word in individual_word_store:
        #calculting the mean danceability of word in all decades, if the word has more than 10 occurences
        if(len(individual_word_store[word]) > 10):
            average = sum(individual_word_store[word]) / len(individual_word_store[word])
            rounded_average = round(average, 2)
            # add the word, danceability, decade and count to the df_count_by_decade dataframe
            df_count_by_word.loc[len(df_count_by_word.index)] = [word, rounded_average, len(individual_word_store[word])]
    return df_count_by_decade, df_count_by_word


def get_top_10_words_by_decade(df_count_by_decade):
    decades = ['1920', '1930', '1940', '1950', '1960', '1970', '1980', '1990', '2000', '2010']
    max_count = 5 #lower limit for removing words with low count
    mean_dance_by_decade = defaultdict(list) # dictionary to store the top 10 words by danceability in each decade
    
    for decade in decades:
        df_decade = df_count_by_decade[df_count_by_decade['decade'] == int(decade)]
        #find max count
        max_count_dec = df_decade['count'].max() #getting the max count of a word in the decade
        
        if max_count_dec > max_count: #if the max count is greater than the lower limit, filter the dataframe
            max_conut_tmp = max_count
            df_decade_filtered = df_decade[df_decade['count'] > max_conut_tmp]
            while len(df_decade_filtered) < 10 and len(df_decade_filtered) < len(df_decade): #if the filtered dataframe has less than 10 words, keep filtering with a lower count limit
                df_decade_filtered = df_decade[df_decade['count'] > (max_conut_tmp-1)]
                max_conut_tmp -= 1
            df_decade = df_decade_filtered
        
        #sort the dataframe by danceability so the top 10 words can be found at the top
        df_decade = df_decade.sort_values(by='danceability', ascending=False)
        #get the top 10 word and danceability like (word, danceability)
        top_words_danceability = []
        if(len(df_decade) < 10):
            for i in range(len(df_decade)):
                top_words_danceability.append((df_decade.iloc[i]['word'], df_decade.iloc[i]['danceability']))
            for i in range(10-len(df_decade)):
                top_words_danceability.append((None, None))
        else:
            for i in range(10):
                top_words_danceability.append((df_decade.iloc[i]['word'], df_decade.iloc[i]['danceability']))
        mean_dance_by_decade[decade] = top_words_danceability
    df_mean_dance_by_decade = pd.DataFrame(mean_dance_by_decade)
    return df_mean_dance_by_decade