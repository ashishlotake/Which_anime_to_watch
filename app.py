import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import datetime
import numpy as np
import math
import seaborn as sns

## Website heading

st.markdown("""
    ## :fire: Which Anime to watch ? 
    [![Twitter](https://img.shields.io/twitter/url?label=Twitter&style=social&url=https%3A%2F%2Ftwitter.com%2Fnainia_ayoub)](https://www.twitter.com/Ashish02lotake)
    [![Linkedin](https://img.shields.io/twitter/url?label=Linkedin&logo=linkedin&style=social&url=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fayoub-nainia%2F%3Flocale%3Den_US)](https://www.linkedin.com/in/ashish-lotake/?locale=en_US)
    [![GitHub](https://img.shields.io/twitter/url?label=Github&logo=GitHub&style=social&url=https%3A%2F%2Fgithub.com%2Fnainiayoub)](https://github.com/ashishlotake)

    I will give you a random anime based on your selected option, btw 90% of animes have less than 39 episodes, so you can easily finish an anime in weekend.
""")


### 1. ----> loading data
data_url = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json" 
@st.cache(allow_output_mutation=True)
def load_data(url):
    r = requests.get(url)
    data = r.json()
    return data

# data_load_state = st.text('Loading data...')
df_1 = pd.DataFrame(load_data(data_url)["data"])
# data_load_state.text("Done!")

### 2.
# getting current year, to give random values for all those anime, which dont have year
current_year = datetime.datetime.now().year

def anime_year(x):
    '''
    This will return the anime year
    
    if year is not given then, it will give random year between 1907 to current year
    '''
    v = list(x.values())
    if type(v[-1]) == int:
        return v[-1]
    else:
        return np.random.randint(1907, current_year)
        # if the year is not given, i will give that anime any year randomly between current year and the least year

df_1["year"] =  df_1["animeSeason"].apply(anime_year)
def git_source(x): return x[0]
df_1["sources"]= df_1["sources"].apply(git_source)
df_1.title = df_1.title.apply(lambda x : x.lower())

### defining another dataframe, to show only limited/useful imformation to the user
df_2 = df_1[["title", "type", "episodes", "status", "tags","picture","year","sources"]].copy()

st.subheader("Lets have a look at dataset")
### year slider, to make the dataframe more interactive for user

# max year for slider
max_year = max(df_2["year"])

year_user = st.slider("", 1907, max_year)

## dataframe
df_user = df_2[["title", "type", "episodes", "status","year"]]

show_user = df_user[((df_user["year"] == year_user ))]
st.dataframe(show_user)

st.caption(f"Total {len(df_1)} animes and constantly updating .....")

## plot--> vizulatization
fig = plt.figure(figsize=(8, 3))
sns.set()
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_color_codes()
sns.set_theme(style="whitegrid", rc=custom_params)

sns.histplot(data=df_2, x="year", binwidth=1, kde=True, alpha=1,color="b")
plt.ylabel("Anime Count")
plt.xlabel("Year")

plt.axvline(x = year_user,color="y",linewidth=3, animated=True)
vv = df_2[df_2["year"]==year_user]
st.write(str(len(vv)), "animes released in ", str(year_user))
plt.axhline(y=len(vv),color="r", linewidth=1, label="fvs")
st.pyplot(fig)
st.caption("As we can see that this is LEFT/NEGATIVE SKEWED histogram, large number of animes were released after 2005")

## percentage text
st.subheader("Before selecting your preference, have a look at this!")

for i in [90,95, 99,99.5,99.9]:
    st.write(i," percent of animes have less than ",math.trunc(np.percentile(df_2['episodes'], i)), " episodes, which equals to ", math.trunc(math.trunc(np.percentile(df_2['episodes'], i)) * 24/60), " hours")


### 3. --- Tags for user
df_2["tags"]=  df_2.tags.apply(lambda x : ",".join(x)) 
# converting the list to string

tags = df_1["tags"]
set_tags = []
for i in tags:
    set_tags.extend(list(i))
    
set_tags = sorted(set(set_tags))

f_set_tag = []
for i in set_tags:
    f_set_tag.extend(i.split(" "))
    
f_set_tag = sorted(set(f_set_tag))

## list of useless tags (stop word)
stop_word = "for gag gap garde ghibli gore gyaru inseki kamis koalas pve pvp pov the time tone uta wall all ai an be bl cg co fi gl go h ii in it me no of on or to tv 2 a & (female) (male) - -- age art bar big boy die ice law man art bar big boy die ice law man 15th 16th 17th 18th 19th into debt feet guro inns loli maso miko mina noir sado scat shop skin skip slow smut solo stop suit vore when with"
stop_word = stop_word.split(" ") 
for i in stop_word:
    if i in f_set_tag:
        f_set_tag.remove(i)


st.subheader("Lets start finding an anime for you")
## multipel tags selector
label = "select multiple genre" ## tell user what he is selecting for 
opt_def = ["cartoon","shounen","manga","anime"] ## if user dosen't select anything, default options
user_tags = st.multiselect(label, f_set_tag,opt_def)


## ask user to define the number of episode the anime should have
user_episode = st.slider("Select the number of episode the anime should have.", 1, 3000, 52)
st.caption(f"1 episode = 24 mins; therefore {user_episode} episodes is approx {math.trunc(user_episode*24/60)} hours")

## select the "greater" or "less" than or "equal" to
user_var = st.selectbox(f"Greater Than or Smaller Than or Equal to {user_episode}" ,("Less", "Greater", "Equal"))

## Ask the user about the status of anime 
user_status = st.selectbox(f"Status of Anime",("ONGOING", "FINISHED","UPCOMING"))



### 4. --- final function, which gives one random anime, based on user input

def show_anime_db(tag:str, episode_number=52, var="less",status="FINISHED" ,no_of_anime=1 ):
    '''
    tag =--> list of tags
    
    status = {"ONGOING", "FINISHED","UPCOMING" }
    var = {"equal", "less", "greater"}
    tag = check 
    no_of_anime = number of anime to show based on your preference --- default =1
    
    return df of anime less than x number of episoded
    '''
    tags = "|".join(tag)
    
    if var == "Equal":
        return df_2[((df_2["episodes"] == episode_number) & (df_2["tags"].str.contains(tags)) & (df_2["status"] == status) )][["title","type","episodes","status","tags","year","picture","sources"]].sample(no_of_anime)
    elif var == "Less":
        return df_2[((df_2["episodes"] <= episode_number) & (df_2["tags"].str.contains(tags)) & (df_2["status"] == status) )][["title","type","episodes","status","tags","year","picture","sources"]].sample(no_of_anime)
    elif var == "Greater":
        return df_2[((df_2["episodes"] >= episode_number) & (df_2["tags"].str.contains(tags)) & (df_2["status"] == status) )][["title","type","episodes","status","tags","year","picture","sources"]].sample(no_of_anime)


try:

    f_db = show_anime_db(tag=user_tags, episode_number=user_episode, var= user_var, status=user_status)
    f_db["hour"] = math.trunc(f_db["episodes"].iloc[0]*24/60)
    st.success("Your Anime is here")
    st.header(f_db["title"].iloc[0])
    st.dataframe(f_db[["type", "episodes","hour" ,"status","year"]])
    img_url = f_db["picture"].iloc[0]
    st.image(img_url)
    info_url = f_db["sources"].iloc[0]
    st.caption(f_db["tags"].iloc[0])
    text_ = "More Info [Click here]({link})".format(link=info_url)
    st.markdown(text_,unsafe_allow_html=True)
    # st.balloons()



except ValueError:
    st.warning("Please select different option, Try changing number of episodes or status of anime or slecting more tags")
