import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date



BASE_URL="https://www.99acres.com/search/property/buy/residential-all/bangalore?search_type=QS&refSection=GNB&search_location=CP20&lstAcn=CP_R&lstAcnId=20&src=CLUSTER&preference=S&selected_tab=1&city=20&res_com=R&property_type=R&isvoicesearch=N&keyword=Bangalore&strEntityMap=IiI%3D&refine_results=Y&Refine_Localities=Refine%20Localities&action=%2Fdo%2Fquicksearch%2Fsearch&searchform=1&price_min=null&price_max=null"
HEADERS={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}

### Get the number of properties present
def getTotalProperties(base_url):
    response=requests.get(base_url,headers=HEADERS)
    soup=BeautifulSoup(response.content)
    #print(soup)
    total_properties=soup.find("div",attrs={'class':'title_semiBold r_srp__spacer20'}).text.split("|")[0]
    total_properties=total_properties.strip('"').split(" ")[0]


    return total_properties


def getAllPageURL(base_url):
    property_data_list=[]
    total_properties=int(getTotalProperties(base_url))
    print("Total Properties "+str(total_properties))
    num_pages=total_properties//30
    if total_properties%31!=0:
        num_pages=num_pages+1
    urls=[]
    urls.append(base_url)
    for i in range(0,num_pages):
        temp_url=base_url
        temp_url=temp_url+"&page_size=30&page="+str(i+1)
        urls.append(temp_url)
    print("Number of URLS "+str(len(urls)))
    for url in urls:
        print(url)
        data=getAllProperties(url)
        property_data_list.append(data)
    property_data=pd.concat(property_data_list)
    print("Total properties extracted")
    print(property_data.shape)
    return property_data











def getAllProperties(url):
    response=requests.get(url,headers=HEADERS)
    soup=BeautifulSoup(response.content)
    properties_tag=soup.findAll("div",attrs={"class":"pageComponent srpTuple__srpTupleBox srp"})
    property_list=[]
    print(len(properties_tag))
    for prop_tag in properties_tag:
        dat=getPropertyDetails(prop_tag)
        #print(dat.shape)
        property_list.append(dat)

    data=pd.concat(property_list)
    print(data.shape)
    return data

def getPropertyDetails(prop_tag):

    #print(prop_tag)
    #with open('prop.txt', 'w', encoding='utf-8') as f_out:
        #f_out.write(prop_tag.prettify())
    prop_id=prop_tag['id']
    prop_desc=prop_tag.find("div",attrs={"class":'body_med'}).text
    prop_title=prop_tag.find("a",attrs={"id":"srp_tuple_property_title"}).text
    society=prop_tag.find("td",attrs={"id":"srp_tuple_society_heading"}).text
    url_tag=prop_tag.find("td",attrs={"id":"srp_tuple_society_heading"})
    if url_tag.find("a")!=None:
        url=url_tag.find("a")["href"]
    else:
        url=""
    price_tag=prop_tag.find("td",attrs={"id":"srp_tuple_price"}).text
    if prop_tag.find("div",attrs={"id":"srp_tuple_price_per_unit_area"})!=None:
        price_per_sq_ft=prop_tag.find("div",attrs={"id":"srp_tuple_price_per_unit_area"}).text
    else:
        price_per_sq_ft=""



    price_tag=price_tag.replace(price_per_sq_ft,"")
    primary_area=prop_tag.find("td",attrs={'id':"srp_tuple_primary_area"}).text
    sec_area=prop_tag.find("div",attrs={"id":"srp_tuple_secondary_area"}).text
    primary_area=primary_area.replace(sec_area,"")
    if prop_tag.find("td",attrs={"id":"srp_tuple_bedroom"})!=None:
        number_bedrooms=prop_tag.find("td",attrs={"id":"srp_tuple_bedroom"}).text
    else:
        number_bedrooms="Missing"
    if prop_tag.find("div",attrs={"id":"srp_tuple_bathroom"})!=None:
        number_bathrooms=prop_tag.find("div",attrs={"id":"srp_tuple_bathroom"}).text
    else:
        number_bathrooms="Missing"
    if number_bedrooms!="Missing":
        if number_bathrooms!="Missing":
            number_bedrooms=number_bedrooms.replace(number_bathrooms,"")

    if prop_tag.find("td",attrs={"class":"srpTuple__tupleBadges"})!=None:
        features_tags=prop_tag.find("td",attrs={"class":"srpTuple__tupleBadges"})
        div_tags=features_tags.findAll("div")
        features=[]
        for tag in div_tags:
            text=tag.text
            text=text.replace(" ","_")
            text=text.strip("_")
            features.append(text)
        features=list(set(features))
        features=" ".join(features)

    else:
        features=""
    builder_info=prop_tag.find("div",attrs={"class":"srpTuple__srpDealerInfoWrap"}).contents
    span_builder_info=builder_info[0].findAll("span")
    date_posted=""
    if builder_info[0].find("a")!=None:
        builder=builder_info[0].find("a").text
    else:
        builder=""
    for span in span_builder_info:
        if "Posted on" in span.text:
            date_posted=span.text
            date_posted=date_posted.replace("Posted on","")
            date_posted=date_posted.replace("by","")
            date_posted=date_posted.strip()

    #print("Builder :"+builder)
    #print(date_posted)




    #print(builder_info)










    '''
    print("Property Title")
    print(prop_title)
    print("Society")
    print(society)
    print("Price")
    print(price_tag)
    print("Price Per Sq Ft")
    print(price_per_sq_ft)
    print("Primary Area")
    print(primary_area)
    print("Sec Area")
    print(sec_area)
    print("Number of Bedrooms")
    print(number_bedrooms)
    print("Number of Bathrooms")
    print(number_bathrooms)
    print("Features")
    print(features)
    #print(prop_desc)
    print(url)
    '''
    data={'property_id':prop_id,'property_title':prop_title,'society':society,'price':price_tag,'price_per_sq_ft':price_per_sq_ft,"primary_area":primary_area,
    'secondary_area':sec_area,"num_bedrooms":number_bedrooms,"num_bathrooms":number_bathrooms,'features':features,'builder':builder,"posted_on":date_posted,
    'scrapped_date':date.today(),'description':prop_desc,'property_url':url}
    dat_list=[]
    dat_list.append(data)
    data=pd.DataFrame(dat_list)
    #print(data.shape)
    return data
    '''
    data=pd.DataFrame()
    data['property_id']=list(prop_id)
    data['property_title']=list(prop_title)
    data['society']=list(society)
    data['price']=list(price_tag)
    data['price_per_sq_ft']=list(price_per_sq_ft)
    data['primary_area']=list(primary_area)
    data['secondary_area']=list(sec_area)
    data['num_bedrooms']=list(number_bedrooms)
    data['num_bathrooms']=list(number_bathrooms)
    data['features']=list(features)
    data['builder']=list(builder)
    data['posted_on']=list(date_posted)
    data['scrapped_date']=list(date.today())
    data['description']=list(prop_desc)
    data['prop_url']=list(url)
    return data
    '''



if __name__ == '__main__':
    data=getAllPageURL(BASE_URL)
    print(data.shape)
    data.to_excel("Property_Bangalore.xlsx",encoding="utf-8",index=False)
    #print(getTotalProperties(base_url))
