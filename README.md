# 📺 TubeTranscript Clone

TubeTranscript Clone est une application web basée sur une architecture microservices permettant d'extraire facilement les sous-titres (transcriptions) de vidéos YouTube. Elle supporte les sous-titres manuels et générés automatiquement, avec traduction et horodatage.

## 🚀 Fonctionnalités

- **Extraction de transcriptions** : Récupère le texte complet d'une vidéo YouTube via son URL ou son ID.
- **Support Multi-langues** :
  - Détection automatique des langues disponibles (Manuelles et Générées).
  - Traduction automatique vers la langue cible si nécessaire.
- **Horodatage (Timestamps)** : Option pour inclure les timestamps `[MM:SS]` devant chaque segment de texte.
- **Interface Utilisateur Intuitive** : Interface simple et réactive construite avec Streamlit.
- **Export** : Téléchargement du transcript au format `.txt`.

## 🏗️ Architecture

Le projet est divisé en deux microservices conteneurisés :

1.  **Backend (`/backend`)** :
    - API REST construite avec **FastAPI**.
    - Utilise `youtube-transcript-api` pour récupérer les données.
    - Expose des endpoints pour lister les langues et récupérer le texte.
2.  **Frontend (`/frontend`)** :
    - Interface utilisateur construite avec **Streamlit**.
    - Communique avec le backend via requêtes HTTP.

## 🛠️ Prérequis

- **Docker** et **Docker Compose** installés sur votre machine.

## 📦 Installation et Démarrage

1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/Dorsumsellae/youtube_transcript_clone.git
    cd youtube_transcript_clone
    ```

2.  **Lancer l'application avec Docker Compose** :
    ```bash
    docker compose up --build
    ```

3.  **Accéder à l'application** :
    - Frontend : Ouvrez votre navigateur sur [http://localhost:8501](http://localhost:8501)
    - Backend API Docs (Swagger) : [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 Utilisation

1.  Collez l'URL d'une vidéo YouTube dans le champ dédié.
2.  L'application détecte automatiquement les langues disponibles.
3.  Sélectionnez la langue souhaitée dans la liste déroulante (les langues générées automatiquement sont indiquées par 🤖).
4.  Cochez "Inclure les timestamps" si vous souhaitez avoir le minutage.
5.  Cliquez sur "Extraire le texte".
6.  Copiez le texte ou téléchargez-le via le bouton "Télécharger .txt".

## 💻 Stack Technique

- **Python 3.9+**
- **FastAPI** (Backend)
- **Streamlit** (Frontend)
- **Docker & Docker Compose**
- **YouTube Transcript API**

## 📝 Licence

Ce projet est un Proof of Concept (PoC) à des fins éducatives.
