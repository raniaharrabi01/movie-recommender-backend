import pandas as pd
import joblib
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from database.mongo import items_collection 

# Nettoyage du texte
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text

# Chargement des données
def load_data():
    docs = list(items_collection.find({}))  # Utiliser la collection importée
    print("📊 Nombre de documents récupérés depuis MongoDB :", len(docs))
    films = []
    for doc in docs:
        film = {
            "id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "genres": " ".join(doc.get("genres", [])),
            "cast": " ".join(doc.get("cast", [])),
            "director": doc.get("director", "") or "",
            "overview": doc.get("overview", "")
        }
        films.append(film)
    return pd.DataFrame(films)

# Combinaison des champs texte
def create_combined_features(df):
    df.fillna("", inplace=True)
    df["combined"] = (
        df["title"] + " " +
        df["genres"] + " " +
        df["cast"] + " " +
        df["director"] + " " +
        df["overview"]
    ).apply(clean_text)
    return df

# Embedding SBERT
def embed_text(texts):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=True)
    joblib.dump(model, "app/ai/model/sbert_model.pkl")
    return embeddings

# Fonction principale
def prepare_data():
    df = load_data()
    df = create_combined_features(df)
    embeddings = embed_text(df["combined"].tolist())
    df.to_csv("app/ai/model/processed_movies.csv", index=False)
    np.save("app/ai/model/embeddings.npy", embeddings)
    print("✅ Données encodées avec SBERT et sauvegardées.")
    print("Nombre de films chargés :", len(df))
    return df, embeddings

# Exécution directe
if __name__ == "__main__":
    prepare_data()
