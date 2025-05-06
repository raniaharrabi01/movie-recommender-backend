import joblib
import pandas as pd

def recommend_movies(query_id, n=5):
    # Charger les fichiers
    df = pd.read_csv("app/ai/model/processed_movies.csv")
    tfidf_matrix = joblib.load("app/ai/model/tfidf_matrix.pkl")
    model = joblib.load("app/ai/model/knn_model.pkl")
    query_id = int(query_id)  # Convert to integer
    # Trouver l'index du film demandé par ID
    if query_id not in df["id"].values:
        return f"❌ Film avec l'ID {query_id} non trouvé dans les données."

    idx = df[df['id'] == query_id].index[0]

    # Trouver les n films les plus similaires
    distances, indices = model.kneighbors(tfidf_matrix[idx].reshape(1, -1), n_neighbors=n+1)

    # Ignorer le premier (le film lui-même)
    recommended_indices = indices.flatten()[1:]
    recommended_distances = distances.flatten()[1:]
    """
    recommended_movies = []
    for i, movie_idx in enumerate(recommended_indices):
        movie = df.iloc[movie_idx]
        recommended_movies.append({
            "id": movie["id"],
            "title": movie["title"],
            "overview": movie["overview"],
            "distance": float(recommended_distances[i])
        })
    """
    # Retourner uniquement les IDs des films recommandés
    recommended_ids = [int(df.iloc[movie_idx]["id"]) for movie_idx in recommended_indices]
    return recommended_ids

# Exemple de test
if __name__ == "__main__":
    # Test avec un ID exemple
    results = recommend_movies(38575, n=4) 
    for movie_id in results:
        print("🎬 ID:", movie_id)
        print("-" * 40)