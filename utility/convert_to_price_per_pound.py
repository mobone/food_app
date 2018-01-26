import pandas as pd
pd.option_context('display.max_rows', None, 'display.max_columns', 3)
df = pd.read_csv('test_data.csv')
df = df[df['Calories ']>0]

#df = df[( df['Product Size'].str.contains('LB') ) | ( df['Product Size'].str.contains('OZ') ) ].copy()
df = df[~df['Product Name'].str.contains('Flour')]
df = df[df['Servings Per Container ']!=999]
df = df[df['Calories ']!=999]
#df['Product Price Per Unit'] = df['Product Price Per Unit'].str.replace(' / LB','')
#df['Product Price Per Unit'] = df['Product Price Per Unit'].str.replace('$','')
#df['Product Size'] = df['Product Size'].str.replace('LB','')

df = df[df['Servings Per Container ']<100]


#df['Product Size'] = pd.to_numeric(df['Product Size'])
for col in df.columns[5:]:
    df[col] = (df[col]*df['Servings Per Container '])/df['Product Price']

#df = df.sort_values(by='Protein ', ascending=False)
del df['Servings Per Container ']
del df['Product Size']
del df['Product Price Per Unit']
print(df.head())
df.to_csv('normalized_test_data.csv')
