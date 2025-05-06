import joblib
from sklearn.neighbors import NearestNeighbors
import pandas as pd

def train_knn_model():
    # Charger les données vectorisées
    tfidf_matrix = joblib.load("app/ai/model/tfidf_matrix.pkl")
    df = pd.read_csv("app/ai/model/processed_movies.csv")

    # Entraîner le modèle KNN
    model = NearestNeighbors(metric="cosine", algorithm="brute")
    model.fit(tfidf_matrix)

    # Sauvegarder le modèle  
    joblib.dump(model, "app/ai/model/knn_model.pkl")
    print("✅ Modèle KNN entraîné et sauvegardé.")

if __name__ == "__main__":
    train_knn_model()
