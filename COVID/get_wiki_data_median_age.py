import requests
from bs4 import BeautifulSoup
import pandas as pd

'''
The COVID-19 is supposed to affect the older population more than the younger population.
While the mortality rate of the corona virus is 0.1% for the younger population, for the older population it is 1/5 or 1/7
This is one of major causes of high death rate in Italy.

So, one key thing to understand is the average age of the population to forecast the spread of COVID.

To get this data we will scrap data from https://en.wikipedia.org/wiki/List_of_countries_by_median_age and then map it to the COVID dataset
'''

URL="https://en.wikipedia.org/wiki/List_of_countries_by_median_age"

def requestData(url):
    response=requests.get(url,headers={"Content-Type": "application/json"})
    print(response.status_code)
    return response.text


def extractMedianAge(response_text):
    soup=BeautifulSoup(response_text)
    #print(soup)
    df=pd.DataFrame()
    table_data=soup.find("table")
    print(table_data)

    columns_data=table_data.findAll("th")
    columns=[column_data.text.strip() for column_data in columns_data]
    print(columns)
    #df.columns=["country","rank","median_age","median_age_male","median_age_female"]

    rows_data=table_data.findAll("tr")
    country=[]
    rank=[]
    median_age=[]
    median_age_male=[]
    median_age_female=[]
    rows_data=rows_data[1:]
    for row_data in rows_data:
        print(row_data)
        tds=row_data.findAll("td")
        print(tds)
        country.append(tds[0].text)
        rank.append(tds[1].text)
        median_age.append(tds[2].text)
        median_age_male.append(tds[3].text)
        median_age_female.append(tds[4].text)
    df['country']=country
    df['rank']=rank
    df['median_age_female']=median_age_female
    df['median_age_male']=median_age_male
    df['median_age']=median_age
    return df







if __name__=='__main__':
    df=extractMedianAge(requestData(URL))
    df.to_excel("Median_Age_By_Country.xlsx",encoding="utf-8",index=False)
