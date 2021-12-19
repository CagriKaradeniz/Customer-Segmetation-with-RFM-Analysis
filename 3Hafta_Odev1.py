import datetime as dt

import pandas as pd
import numpy as np
import Utils_cagri as util
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#Görev 1

#Soru1:Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.

df_=pd.read_excel("online_retail_II.xlsx",sheet_name="Year 2010-2011")
data=df_.copy()
data.head()

#Soru2:Veri setinin betimsel istatistiklerini inceleyiniz.
data.shape
data.head()
data.tail()
data.describe().T

util.dataset_ozet(data)

#Soru3:Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
util.dataset_ozet(data)
data.isnull().sum()

#Soru4:Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.

data.dropna(inplace=True)
data.shape
data.isnull().sum()

#Soru5:Eşsiz ürün sayısı kaçtır?

data.Description.nunique()
print(f"Eşsiz ürün sayısı: {data.Description.nunique()}")

#Soru6:Hangi üründen kaçar tane vardır?

data.Description.value_counts()

#Soru7:En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.

data.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(5)

#Soru8:Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
data.shape
data=data[~data["Invoice"].str.contains("C",na=False)]
data.shape
#Soru9:Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
data["TotalPrice"]=data["Quantity"]*data["Price"]
data.head()
util.dataset_ozet(data)

#Görev 2
#RFM metriklerinin hesaplanması
#Recency, Frequency ve Monetary tanımlarını yapınız.

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

#GÖREV 3
#RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

rfm["Frequency_Score"]=pd.qcut(rfm["Frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rfm["Recency_Score"]=pd.qcut(rfm["Recency"],5,labels=[5,4,3,2,1])
rfm["Monetary_Score"]=pd.qcut(rfm["Monetary"],5,labels=[1,2,3,4,5])
rfm.head()
rfm["RFM_Score"]=rfm.Recency_Score.astype(str)+rfm.Frequency_Score.astype(str)


#GÖREV 4
#RFM skorlarının segment olarak tanımlanması

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

#GÖREV 5
#Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# Hem aksiyon kararları açısından,
# Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.
#"Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.

cıktı=rfm[rfm["Segment_Class"]=="loyal_customers"]
cıktı.to_excel("Loyal_Customers.xlsx",sheet_name="Hafta3_Odev1_Görev5")

util.categoric_ozet(rfm,"Segment_Class",True,True)

#Bu tabloya göre müşterilerin %57'lik kesimini hibernating loyal customers ve champions sınıfı oluşturuyor.

rfm.groupby("Segment_Class")[["Recency","Frequency","Monetary"]].agg(["mean","sum"])
karsilastirma_tablo=rfm.groupby("Segment_Class")[["Recency","Frequency","Monetary"]].agg(["mean","sum"])

#Bu tabloya baktığımızda ise ortalama en fazla gelir sağlanan 3 grup champions, loyal customers ve can't loose sınıfı.
#Aynı zamanda tabloyu incelediğimizde alış veriş sıklığında  ilk 3 grup sırasıyla champions ,can't loose ve loyal customers.
#Tabloda REcency bakımından en kötü 3 grup sırasıyla hibernating,at_Risk ve can't loose


#SONUÇ Yorumum: MEvcut müşteri ve fiyat politikalarına göre Champions ve loyal_customers sınıflarının çok sık alış veriş yaptığı
# ve ortalama kazancın yüksek olduğu görülüyor. Şirketin daha çok kazanç sağlması için bu iki sınıf hacminin büyümesi gerekmektedir.
#can't loose grubunun ortalama kazanç değeri çok yüksek fakat son alış veriş tarihleri çok eskide kalmış. Bu grubu analiz ederek,
#bu müşteri grubuna özel kampanyalar sağlanarak müşteriler geri kazanılabilir ve bu sınıfı champions sınıfına kaydırabiliriz.
#Potential_loyallist grubunun ise alışveriş frekans sıklığını artırarak bu sınıfı loyal customers sınıfına kaydırabiliriz.
#Bu gruba uygun analiz yapılması ve bu grubun tercih ettiği ürünlerin çeşitlendirilmesi ve indirimler yapılması sağlanmalıdır.
#Son olarak at_Risk grubunun  ortalama kazancı ve frekansı hatrı sayılır seviyelerde. Son alışveriş zamanları hayli eski.
#Bu gruplara gerekirse iletişim bilgileri ile ulaşılıp hediye çekleri verilerek tekrar sisteme kazandırılması gerekiyor.

