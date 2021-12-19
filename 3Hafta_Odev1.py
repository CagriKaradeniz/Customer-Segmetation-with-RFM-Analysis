import datetime as dt

import pandas as pd
import numpy as np
import Utils_cagri as util
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)



#Loading dataset

df_=pd.read_excel("online_retail_II.xlsx",sheet_name="Year 2010-2011")
data=df_.copy()
data.head()

#Data set first analysis
data.shape
data.head()
data.tail()
data.describe().T

util.dataset_ozet(data)

#Null Value control and drop
util.dataset_ozet(data)
data.isnull().sum()
data.dropna(inplace=True)
data.shape
data.isnull().sum()

#Unique Product number

data.Description.nunique()
print(f"Unique Product number : {data.Description.nunique()}")
data.Description.value_counts()

#Most popular products

data.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(5)

#Drop cancaled invoices
data.shape
data=data[~data["Invoice"].str.contains("C",na=False)]
data.shape
#Soru9:Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
data["TotalPrice"]=data["Quantity"]*data["Price"]
data.head()
util.dataset_ozet(data)

#RFM Parameters Recency, Frequency ve Monetary.

today=dt.datetime(2011,12,11)
rfm=data.groupby("Customer ID").agg({"Invoice":lambda x: x.nunique() ,
                                 "InvoiceDate":lambda x: (today-x.max()).days,
                                 "TotalPrice":lambda x: x.sum()
                                 })
rfm.head()
rfm.columns=["Frequency","Recency","Monetary"]
rfm.head()
rfm.shape
rfm=rfm[rfm["Monetary"]>0]
rfm.shape

#Creating RFM Score parameters

rfm["Frequency_Score"]=pd.qcut(rfm["Frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rfm["Recency_Score"]=pd.qcut(rfm["Recency"],5,labels=[5,4,3,2,1])
rfm["Monetary_Score"]=pd.qcut(rfm["Monetary"],5,labels=[1,2,3,4,5])
rfm.head()
rfm["RFM_Score"]=rfm.Recency_Score.astype(str)+rfm.Frequency_Score.astype(str)



#Split segments according to RFM Score parameters

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm["Segment_Class"]=rfm["RFM_Score"].replace(seg_map,regex=True)
rfm.head()


#FINAL
#Analysis of each segments
util.categoric_ozet(rfm,"Segment_Class",True,True)
rfm.groupby("Segment_Class")[["Recency","Frequency","Monetary"]].agg(["mean","sum"])
karsilastirma_tablo=rfm.groupby("Segment_Class")[["Recency","Frequency","Monetary"]].agg(["mean","sum"])



