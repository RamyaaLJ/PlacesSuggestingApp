"""
Code Developed and Modified By : Nishant Pandey
Git Link : https://github.com/unexh/

"""
#importing libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk.tokenize import word_tokenize
import sys

#Linking essentials
csvFileLink = r'NewZomato.csv'
backgroundImageLink = r'images\sizller-with-noodles22.jpg'
searchIconLink = r'images\icons8-search-50(2).png'
backGround2ImageLink= r'images\Sitting-near-table-darkened.jpg'
backButtonImageLink =r'images\icons8-back-50.png'

DataFieldWhole = pd.read_csv(csvFileLink,encoding='latin')

#a class to contain Restaurant Related Data
class RestaurantData:
        #RestaurantData Attributes
        selectedCityName=str("")
        selectedLocalityName=str("")
        selectedRestaurantName=str("")
        DataFieldWhole = pd.read_csv(csvFileLink,encoding='latin')
        tempTopRestaurantDF = None

        #Initializes TopRestuarantDf by calling ReturnTopFiveRestaurantName()
        def __init__(self):
            self.tempTopRestaurantDF = self.ReturnTopFiveRestaurantName()

        #Returns City Name List from Database
        def ReturnCityName(self):
            CityData = list(self.DataFieldWhole['City'].unique())
            CityData.sort()
            return CityData

        #Returns Locality Name List using currentCity from Database
        def ReturnLocalityName(self,currentCity):
            self.selectedCityName = str(currentCity)
            print("SelectedCityName : {}".format(self.selectedCityName))
            DataFieldWholeTemp = self.DataFieldWhole[self.DataFieldWhole['City']==self.selectedCityName]
            localityData = list(DataFieldWholeTemp['Locality'].unique())
            localityData.sort()
            return localityData

        #Returns Restaurant Name List using currentCity,currentLocality from Database
        def ReturnRestaurantName(self,currentCity,currentLocality):
            self.selectedCityName = str(currentCity)
            self.selectedLocalityName = str(currentLocality)
            DataFieldWholeTemp = self.DataFieldWhole[(self.DataFieldWhole['City']==self.selectedCityName) & (self.DataFieldWhole['Locality']==self.selectedLocalityName)]
            RestaurantData = list(DataFieldWholeTemp['Restaurant Name'].unique())
            RestaurantData.sort()
            return RestaurantData

        #Recommendation Function for Calculation of Cosine Similarity Score
        def RestaurantRecommendFunc(self,location,title):
            data_sample = self.data_new_delphi.loc[self.data_new_delphi['Locality'] == location] # data frame

            # index will be reset for cosine similarty index because Cosine similarty index has to be same value with result of tf-idf vectorize
            data_sample.reset_index(level=0, inplace=True)
            #print(data_sample)

            #Feature Extraction
            data_sample['Split']='X'
            for i in range(0,data_sample.index[-1]+1):
                split_data=re.split(r'[,]', data_sample['Cuisines'][i])
                for k,l in enumerate(split_data):
                    split_data[k]=(split_data[k].replace(" ", ""))
                split_data=' '.join(split_data[:])
                data_sample['Split'].iloc[i]=split_data
                
            ## --- TF - IDF Vectorizer---  ##
            #Extracting Stopword
            tfidf = TfidfVectorizer(stop_words='english')

            #Replace NaN for empty string
            data_sample['Split'] = data_sample['Split'].fillna('')

            # Applying TF-IDF Vectorizer
            tfidf_matrix = tfidf.fit_transform(data_sample['Split'])
            tfidf_matrix.shape

            # Using for see Cosine Similarty scores
            feature= tfidf.get_feature_names_out()

            ## ---Cosine Similarity--- ##()
            # Compute the cosine similarity matrix
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

            # Column names are using for index
            corpus_index=[n for n in data_sample['Split']]

            #Construct a reverse map of indices
            indices = pd.Series(data_sample.index, index=data_sample['Restaurant Name']).drop_duplicates()
            #print(indices)

            #index of the restaurant matchs the cuisines
            idx = indices[title]

            #Aggregate rating added with cosine score in sim_score list.
            sim_scores=[]
            for i,j in enumerate(cosine_sim[idx]):
                k=data_sample['Aggregate rating'].iloc[i]
                if j != 0 :
                    sim_scores.append((i,j,k))

            #Sort the restaurant names based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: (x[1],x[2]) , reverse=True)

            # 5 similarty cuisines
            sim_scores = sim_scores[1:6]

            rest_indices = [i[0] for i in sim_scores]

            data_x =data_sample[['Restaurant Name','Cuisines','Aggregate rating']].iloc[rest_indices]

            data_x['Cosine Similarity']=0
            for i,j in enumerate(sim_scores):
                data_x['Cosine Similarity'].iloc[i]=round(sim_scores[i][1],2)
            return data_x.reset_index(drop=True)

        #Returns a DataFrame of RestaurantRecommendFunc
        def ReturnDF(self, cityname, locality, restaurant_name):
            #Remove NULL values from the City column.
            self.DataFieldWhole['City'].value_counts(dropna = False)

            #user selects City : Delhi as most Restaurants are here
            data_city =self.DataFieldWhole.loc[self.DataFieldWhole['City'] == cityname]#user-provided-data
            
            #Now get all the Restaurant Name, Cuisines, Locality, Aggregate rating in Delhi.
            self.data_new_delphi=data_city[['Restaurant Name','Cuisines','Locality','Aggregate rating']]

            #REMOVE Null values from 'Locality' column
            self.data_new_delphi['Locality'].value_counts(dropna = False).head(5)

            #selecting a locality in delhi, 
            self.data_new_delphi.loc[self.DataFieldWhole['Locality'] == 'Connaught Place']

            data_sample=[]
            return self.RestaurantRecommendFunc(locality,restaurant_name)

        #Implements Top restaurant code
        def ReturnTopFiveRestaurantName(self):
            restaurantTopFive = self.DataFieldWhole.sort_values('Weighted Aggregate Rating',ascending=False)
            restaurantTopFive = restaurantTopFive[['City','Locality','Restaurant Name','Aggregate rating','Weighted Aggregate Rating']].head(5)
            restaurantTopFive.reset_index()
            return restaurantTopFive
        
        def ReturnList(self, cityname, locality, restaurant_name):
            resp = []
            rows = self.ReturnDF(cityname, locality, restaurant_name)
            print("rows", rows)
            if not rows.empty:
                for index,row in rows.iterrows():
                    resp.append({
                        "s_no" : str(index+1),
                        "restaurant_name": str(row['Restaurant Name']),
                        "cuisines": str(row['Cuisines']),
                        "rating": str(row["Aggregate rating"]),
                        "cosine_similarity_score": str(row['Cosine Similarity'])
                    })
            else: 
                print("No recommendation")
            
            print("Resp", resp)
        
            return resp        

if __name__ == "__main__":
    import sys#remove
    r = RestaurantData()
    print(r.ReturnCityName())
    print(r.ReturnLocalityName('Coimbatore'))
    print(r.ReturnTopFiveRestaurantName())


"""
Code Developed and Modified By : Nishant Pandey
Git Link : https://github.com/unexh/

"""
