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