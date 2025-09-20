import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.pyplot as plt
df=pd.read_csv("book_store.csv") 
print("📌 df.head():")
print(df.head())

# show general information
print("\n📌 df.info():")
print(df.info())

#summarise data
print("\n📌 df.describe():")
print(df.describe(include="all"))
#find cheap book
print("📌 find quality book")
quality_books = df[(df["opinion"] == "cheap") & (df["rating"].isin(["Five", "Four"]))]
print("quality books in the first 5 rows are:")
print(quality_books.head())
print(f"number of quality books is: {len(quality_books)}")
#summarise by opinion
print('📌 summarize by opinion')
print(df["opinion"].value_counts())
#summarise by category
print("📌 summarize by category:")
print(df["category"].value_counts())
#average money based on rating
print("📌 average money based on rating")
df["price"]=df["price"].str.replace("£", "").astype(float)
print(df.groupby("rating")["price"].mean())
#average money based on category
print(df.groupby("category")["price"].agg(["count", "mean"]))
#find the most popular word in decription
print("📌 Top 10 most inspiring word are: ")
all_words = " ".join(df["description"].dropna()).lower().split() 
word_counts = Counter(all_words) 
print(word_counts.most_common(10))
#bar chart
df["rating"].value_counts().plot(kind="bar",edgecolor="black")
plt.title("Number of books by rating")
plt.xlabel("rating")
plt.ylabel("count")
plt.show() 

#pie chart
opinion_counts = df["opinion"].value_counts()

opinion_counts.plot(
    kind="pie", 
    autopct="%.1f%%", 
    startangle=90, 
    wedgeprops={"edgecolor": "black", "linewidth": 1}
)

plt.title("Book price distribution")
plt.ylabel("")  
plt.legend(opinion_counts.index, title="Opinion")  # thêm legend
plt.show()
#histogram
plt.hist(df["price"], bins=20, edgecolor="black")

# Add mean line
plt.axvline(df["price"].mean(), color="red", linestyle="dashed", linewidth=2, label="Mean")

# Add median
plt.axvline(df["price"].median(), color="green", linestyle="dashed", linewidth=2, label="Median")

plt.title("Price distribution with Mean & Median")
plt.xlabel("Price (£)")
plt.ylabel("Frequency")
plt.legend()
plt.show()
#show the analysed data
print("📌 analysis the price ")
price_bins = pd.cut(df["price"], bins=10)
price_counts = price_bins.value_counts().sort_index()
print(price_counts)
print("the price range with most books:", price_counts.idxmax())
#summarize the category
df["category"].value_counts().head(10).plot(kind="bar", figsize=(10,5))
plt.title("Number of books by category")
plt.xlabel("Category")
plt.ylabel("Count")
plt.show()
#skewness of data
print("Skewness of price:", df["price"].skew())
df["price"].plot(kind="box")
plt.title("Price distribution (Boxplot)")
plt.show()