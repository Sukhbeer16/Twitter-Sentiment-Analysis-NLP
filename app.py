import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# Load dataset 
data = pd.read_csv("tweets_sample.csv")  # Replace with your dataset path
data = data[['tweet', 'sentiment']]

# Simple preprocessing (lowercase, remove mentions & hashtags)
def preprocess(text):
    text = text.lower()
    text = text.replace('@', '')
    text = text.replace('#', '')
    text = text.replace('\n', ' ')
    return text

data['clean_tweet'] = data['tweet'].apply(preprocess)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    data['clean_tweet'], data['sentiment'], test_size=0.2, random_state=42
)

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(max_features=1000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_vec, y_train)

# Streamlit UI 
st.title("Twitter Sentiment Analysis App")
tweet_input = st.text_area("Enter a tweet to analyze:")
if st.button("Predict Sentiment"):
    tweet_vec = vectorizer.transform([tweet_input])
    prediction = rf_model.predict(tweet_vec)[0]
    st.write("Predicted Sentiment:", prediction)
