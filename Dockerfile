# Utilisez une image de base avec le support Python
FROM python:3.10

# Définissez le répertoire de travail
WORKDIR /app

# Copiez le fichier requirements.txt et installez les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste de l'application
COPY . .

# Exposez le port sur lequel votre application Flask écoute
EXPOSE 5000

# Commande pour lancer l'application Flask
CMD ["python", "app.py"]
