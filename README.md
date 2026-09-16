# Livre d'Or Numérique — Dr Béatrice 🐾

Application web commémorative développée en **Svelte + FastAPI + SQLite** pour recueillir et mettre en valeur les témoignages de clients pour le départ en retraite du **Dr Béatrice**.

---

## ✨ Architecture & Confidentialité (2 Frontends Isolés en 1 Conteneur)

Pour préserver la surprise et empêcher toute consultation des messages par les clients avant le jour J, le système sépare strictement la **collecte** et la **consultation** :

1. **Port 81 (Client / Dépôt Témoignages)**
   - Dédié exclusivement aux clients (via QR Code / lien direct).
   - **Aucun moyen de consulter les messages des autres clients** : étanchéité totale, zéro risque de fuite ou de gaffe.
   - Idéal pour être branché sur un sous-domaine public dédié (ex: `https://participer.mondomaine.fr`).

2. **Port 80 (Consultation / Livre d'Or & Pot de départ)**
   - 📖 **Le Livre d'Or** : galerie avec filtres par animal (Chiens, Chats, NACs, Chevaux, Autres) et recherche.
   - 🎬 **Projection Pot de départ** : bouton dédié dans le menu pour lancer immédiatement le diaporama plein écran lors de la fête.
   - 🖨️ **Format Album Papier** : mise en page soignée pour impression HD / PDF imprimeur.
   - 🔒 **Modération Secrète** : accessible uniquement via une URL alphanumérique complexe (`#/admin-k8x7m2q9v3p4z1y`) et protégée par mot de passe.

---

## 🐳 Déploiement Docker

Le projet s'organise en **2 conteneurs indépendants** :
1. `livredor_frontend` : Conteneur Nginx servant les deux frontends isolés (port 80 et port 81).
2. `livredor_backend` : Conteneur FastAPI + SQLite pour l'API et le stockage sécurisé des médias.

---

### 1. Test en Local (localhost)

```bash
docker compose up -d --build
```

- **Consultation & Diaporama** : [http://localhost](http://localhost) (port 80)
- **Dépôt Témoignages Client** : [http://localhost:8081](http://localhost:8081) (port 8081)
- **Espace Modération Secret** : [http://localhost/#/admin-k8x7m2q9v3p4z1y](http://localhost/#/admin-k8x7m2q9v3p4z1y)
- **API Backend** : [http://localhost:8000/docs](http://localhost:8000/docs) (port 8000)

---

### 2. Déploiement NAS Synology (Container Manager / Docker)

Utilisez le fichier `docker-compose-synology.yml` :

```bash
docker compose -f docker-compose-synology.yml up -d --build
```

| Service | Port Externe NAS | Port Interne | Usage / Sous-domaine Reverse Proxy |
| :--- | :--- | :--- | :--- |
| **Frontend Consultation** | **`9083`** | `80` | `livre.mondomaine.fr` |
| **Frontend Dépôt Client** | **`9084`** | `81` | `participer.mondomaine.fr` |
| **Backend API** | **`9003`** | `8000` | API & Stockage médias |

- **Réseau Bridge Synology** : `192.168.53.0/24`
- **Persistance des données** : Base de données dans `./data/` et médias originaux dans `./uploads/`.

---

## 🔐 Configuration des Variables d'Environnement (.env)

Les variables sensibles doivent être définies dans votre fichier `.env` sur le serveur :
- `HONORED_PERSON` : Nom de la personne honorée.
- `ADMIN_PASSWORD` : Mot de passe pour l'espace modération.
- `TEAM_PASSWORD` : Mot de passe réservé à l'équipe clinique pour l'import de photos/vidéos.
- `CLIENT_SECRET_SLUG` : Route secrète d'accès pour les invités (sans le `#`, intégrée automatiquement au QR Code généré dans l'espace modération).
- `SUBMIT_TOKEN` : Jeton technique interne d'autorisation d'API.
