import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

# 1. Load dataset
df = pd.read_csv("UpdatedResumeDataSet.csv")
df = df[['Resume_str', 'Category']]
df.columns = ['resume_text', 'category']

# 2. Vectorize text using TF-IDF
tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
X = tfidf.fit_transform(df['resume_text'])
y = df['category']

# 3. Train classifier
model = MultinomialNB()
model.fit(X, y)

# 4. Save the model and vectorizer using joblib
joblib.dump(model, 'resume_model.pkl')
joblib.dump(tfidf, 'vectorizer.pkl')

print("✅ Model and vectorizer saved successfully!")
