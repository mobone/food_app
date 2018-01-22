import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client['products']
db_collection = db['cub_products']




df = pd.DataFrame(list(db_collection.find({})))


columns = ['Item Number', 'Price', 'Servings Per Container', 'Calories', 'Total Fat', 'Cholesterol', 'Sodium', 'Total Carbohydrate', 'Protein']
df = df[columns]

df['Price'] = df['Price'].str.replace('$','')

for i in df.columns:
    print(i)
    df[i] = df[i].str.replace('m','')
    df[i] = df[i].str.replace('g','')

    df[i] = pd.to_numeric(df[i])
df['Price Per Serving'] = df['Price'] / df['Servings Per Container']
df['Price'] = df['Price Per Serving']
del df['Price Per Serving']
df = df.fillna(0)
print(df)
df.to_csv('test_data.csv', index=False)
