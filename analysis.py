import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
data = pd.read_csv("tweets_sample.csv")  # Replace with actual dataset path
data = data[['tweet', 'sentiment']]

# Simple preprocessing
def preprocess(text):
    text = text.lower()          # Lowercase
    text = text.replace('@', '') # Remove mentions
    text = text.replace('#', '') # Remove hashtags
    text = text.replace('\n', ' ')
    return text

data['clean_tweet'] = data['tweet'].apply(preprocess)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    data['clean_tweet'], data['sentiment'], test_size=0.2, random_state=42
)

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=1000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_vec, y_train)

# Save trained model and vectorizer for Streamlit app
with open("rf_model.pkl", "wb") as model_file:
    pickle.dump(rf_model, model_file)

with open("vectorizer.pkl", "wb") as vec_file:
    pickle.dump(vectorizer, vec_file)
