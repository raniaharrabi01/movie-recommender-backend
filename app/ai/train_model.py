def recommend_movies(user_id):
    # 1. Récupérer toutes les notes de cet utilisateur
    user_ratings = list(ratings_collection.find({"user_id": user_id}))
    rated_item_ids = [str(rating["item_id"]) for rating in user_ratings]
    user_rated_scores = {str(rating["item_id"]): rating["rating"] for rating in user_ratings}
    print("Récupérer tous les user ratings :", len(user_ratings))
    print("Récupérer tous les rating item_ids :", len(rated_item_ids))

    if not user_ratings:
        return jsonify({"message": "L'utilisateur n'a pas encore noté de films."}), 404

    # 2. Récupérer tous les films (notés et non notés)
    all_items = list(items_collection.find())
    print("Récupérer tous les films (notés et non notés) :", len(all_items))

    # 3. Préparer les textes pour TF-IDF (genres + overview) et l’identifiant unique
    documents = []
    item_id_list = []
    for item in all_items:
        genres = " ".join(item.get("genres", []))
        overview = item.get("overview", "")
        text = f"{genres} {overview}"
        documents.append(text)

        # Gérer l'identifiant : 'id' ou '_id'
        item_id = str(item.get("id", item.get("_id")))
        item_id_list.append(item_id)

    print("Récupérer tous les item_id des films :", len(item_id_list))
    print("Récupérer tous les item_id des films :", (item_id_list))

    # 4. Vectoriser avec TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)

    # 5. Séparer X_train (films notés) et X_test (films non notés)
    rated_indices = [i for i, item_id in enumerate(item_id_list) if item_id in rated_item_ids]
    unrated_indices = [i for i, item_id in enumerate(item_id_list) if item_id not in rated_item_ids]

    print("Récupérer tous les films notés :", len(rated_indices))
    print("Récupérer tous les films non notés :", len(unrated_indices))

    # 6. Préparer X_train et y_train
    X_train = X[rated_indices]
    y_train = np.array([user_rated_scores[item_id_list[i]] for i in rated_indices])

    # 7. Entraîner un modèle de régression
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 8. Évaluer le modèle sur les films notés
    y_pred_train = cross_val_predict(model, X_train, y_train, cv=5)

    print("Évaluation sur les films notés :")
    print("R² Score:", r2_score(y_train, y_pred_train))
    print("MAE:", mean_absolute_error(y_train, y_pred_train))
    print("RMSE:", np.sqrt(mean_squared_error(y_train, y_pred_train)))

    # 9. Prédire les notes pour les films non notés
    X_test = X[unrated_indices]
    test_item_ids = [item_id_list[i] for i in unrated_indices]
    predicted_ratings = model.predict(X_test)

    print(predicted_ratings)

    # 10. Sélectionner les films avec une note prédite ≥ 4
    recommended_movies = []
    for idx, pred_rating in enumerate(predicted_ratings):
        if pred_rating >= 4:
            movie_id = test_item_ids[idx]
            movie = next((item for item in all_items if str(item.get("id", item.get("_id"))) == movie_id), None)
            if movie:
                movie["_id"] = str(movie["_id"])
                recommended_movies.append(movie)

    return jsonify(recommended_movies)