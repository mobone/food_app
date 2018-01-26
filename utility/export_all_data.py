import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client['products']
db_collection = db['coborns_products']

df = pd.DataFrame(list(db_collection.find({})))

print(df.columns)
columns = ['Product Name', 'Product Price', 'Product Size', 'Product Price Per Unit', 'Servings Per Container ',
           'Calories ', 'Total Fat ', 'Saturated Fat ', 'Cholesterol ', 'Sodium ',
           'Total Carbohydrate ', 'Dietary Fiber ', 'Protein ', 'Vitamin A ',
           'Vitamin C ', 'Calcium ', 'Iron ']
df = df[columns]

#df['Product Price'] = df['Product Price'].str.replace(' SALE','')
#df['Product Price'] = df['Product Price'].replace('$','')

for i in df.columns[1:]:
    print(i)
    try:
        df[i] = pd.to_numeric(df[i])
    except:
        pass
#df['Price Per Serving'] = df['Price'] / df['Servings Per Container']
#df['Price'] = df['Price Per Serving']
#del df['Price Per Serving']
df = df.fillna(0)
print(df)
df.to_csv('test_data.csv', index=False)
