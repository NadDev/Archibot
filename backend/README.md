# Backend local (B1)

## Objectif
Demarrer en local sans bloquer sur l'hebergement.

## Prerequis
- Python 3.11+

## Installation
1. Creer un environnement virtuel local:
   python -m venv .venv
2. Activer l'environnement virtuel (PowerShell):
   .\.venv\Scripts\Activate.ps1
3. Mettre pip a jour:
   python -m pip install --upgrade pip
4. Installer les dependances:
   python -m pip install -r requirements.txt
5. Copier le fichier d'environnement:
   copy .env.example .env

## Lancement
python -m uvicorn app.main:app --reload --env-file .env

Note:
- Si vous installez hors venv, Windows peut afficher des warnings "script not on PATH".
- Le mode venv evite les conflits de dependances avec les packages globaux.

## Configuration Supabase (D1)
Les endpoints de retrieval, ingestion et assistant exigent un bearer token emis par Supabase Auth. Le backend le valide avec Supabase Auth puis transmet le JWT utilisateur a PostgREST pour que les policies RLS s'appliquent.

 Configurer dans `.env`:
- SUPABASE_URL
 - SUPABASE_PUBLISHABLE_KEY (cle publishable, jamais une cle service dans le frontend)
- ARCHIBOT_CHUNKS_TABLE (optionnel, defaut: chunks)
- ARCHIBOT_CORS_ORIGINS (origines frontend autorisees, separees par des virgules)

 Sans cette configuration, `/health` et `/v1/demo-response` restent disponibles, mais les endpoints proteges repondent 503. Un bearer absent ou invalide est refuse.

Pour le frontend local, autoriser `http://localhost:5173` et `http://127.0.0.1:5173`. En production, remplacer ces valeurs par les origines HTTPS exactes du frontend ; ne pas utiliser `*`.

Dans Supabase Auth, l'email est actif et la confirmation email est actuellement requise. Configurer l'URL du site et les URL de redirection locales/de production. Le formulaire impose 12 caracteres minimum ; aligner aussi la longueur minimale dans les parametres Password d'Auth. Configurer SMTP avant l'ouverture a de vrais utilisateurs pour la delivrabilite des confirmations et des resets.

 ### Perimetres de donnees
 La table privee `chunks` contient au minimum:
- owner_id (uuid, references auth.users.id)
- text (text)
- source_type (text): course | general | local_regulation
- source_id (text)
- project_id (text)
- doc_version (text)
- locality (text, nullable)
- page_number (integer, nullable)
- chunk_index (integer, nullable)
- ingested_at (timestamptz)

Pour une base existante, appliquer `sql/chunk_page_provenance.sql` après `sql/chunks.sql`. Les deux champs sont facultatifs pour les chunks qui ne proviennent pas d'un PDF paginé.

Exemple SQL:

create table if not exists chunks (
   id bigserial primary key,
   owner_id uuid not null references auth.users(id) on delete cascade,
   text text not null,
   source_type text not null,
   source_id text not null,
   project_id text not null,
   doc_version text not null,
   locality text,
   page_number integer check (page_number is null or page_number >= 1),
   chunk_index integer check (chunk_index is null or chunk_index >= 1),
   ingested_at timestamptz not null default now()
);

 Chaque ligne privee est limitee au couple proprietaire/projet par RLS. Les anciennes lignes dont `owner_id` est nul restent inaccessibles jusqu'a ce qu'une attribution explicite et verifiee soit faite ; ne pas les attribuer en masse a un compte arbitraire.

 Le corpus commun de connaissances generales est stocke separement dans `architecture_knowledge_chunks`. Les comptes authentifies peuvent le lire, mais seules les operations d'administration peuvent l'alimenter. L'API utilisateur ne peut pas y inserer de chunks.

## Endpoints initiaux
- GET /health
- GET /v1/demo-response
 - POST /v1/retrieval/search (Bearer Supabase Auth requis)
 - POST /v1/ingestion/chunks (Bearer Supabase Auth requis; chunks prives uniquement)
 - POST /v1/assistant/answer (Bearer Supabase Auth requis)
 - POST /v1/courses/{course_id}/extract (Bearer Supabase Auth requis; cours privé existant)

## Extraction documentaire
- `app/extraction/` contient les parseurs PDF, DOC/DOCX, PPT/PPTX, EPUB et images. PDF : texte natif avec fallback OCR par page ; DOC/PPT binaires : conversion LibreOffice puis parseur moderne ; images : OCR avec localisateur `image`.
- `DocumentChunk` conserve `page_number` pour le PDF et utilise `locator_type`, `locator`, `source_order` pour tous les formats. Les documents reformatables n'ont pas de numéro de page fictif.
- Les limites par défaut sont de 1 200 caractères par chunk avec 160 caractères de recouvrement ; elles sont configurables par appel.
- Les fichiers invalides, vides, protégés ou sans texte extractible sont rejetés avec une erreur explicite. DOCX/PPTX/EPUB sont prévalidés (nombre d'entrées, taille totale décompressée, ratio de compression, chemins et entrées chiffrées). Les images sont limitées à 20 mégapixels ; l'OCR PDF est limité à 30 pages scannées et 12 mégapixels rendus par page.
- RapidOCR/ONNX Runtime et PyMuPDF exécutent l'OCR localement. La reconnaissance peut normaliser ou omettre des accents ; aucune confiance OCR n'est encore persistée. Les images intégrées aux diaporamas, notes de présentation et rapports détaillés par page restent hors périmètre.
- DOC/PPT binaires nécessitent un convertisseur LibreOffice configuré (`LIBREOFFICE_BINARY`) et `ARCHIBOT_ENABLE_LEGACY_OFFICE_CONVERSION=true`. La conversion est désactivée par défaut ; n'activer ce drapeau que pour un worker conteneurisé, non privilégié, sans réseau ni secrets, avec limites CPU/mémoire. Un dossier temporaire, le mode headless, un timeout de 60 secondes et une limite de 50 Mio complètent cette isolation, sans la remplacer. L'environnement de développement actuel n'a pas LibreOffice ; les tests vérifient le protocole avec un convertisseur simulé, pas la conversion réelle.
- `app/upload/courses.py` expose l'extraction d'un cours déjà envoyé dans le bucket privé `user-courses`. Le propriétaire est vérifié et le JWT utilisateur est transmis à Storage et PostgREST.
- Appliquer `sql/course_extraction.sql` après `sql/projects.sql`, `sql/user_courses.sql` et `sql/project_courses.sql`, puis `sql/course_document_locations.sql`. Cette dernière migration préserve les pages PDF existantes, rend la page facultative pour les autres formats, ajoute les localisateurs/formats et élargit l'allowlist MIME privée.
- L'enregistrement des chunks et du statut est transactionnel. Une relance remplace les chunks sans doublons ; une insertion invalide annule la transaction. Un résultat d'échec supprime les anciens chunks et conserve une raison explicite, sans supprimer le fichier.
- Le retrieval inclut les cours sélectionnés dans `project_course_links`, sans copier leurs chunks par projet. `app/extraction/store.py` charge toutes les pages de résultats sous RLS et expose le format/localisateur.
- L'upload frontend déclenche automatiquement l'extraction. Les statuts persistés sont `pending`, `extracted`, `failed`, `unsupported`. « Réessayer » n'apparaît que pour un format extractible en attente, en échec ou marqué non pris en charge avant le déploiement du parseur.
- L'extraction est synchrone et limitée à 50 Mio par fichier. Le frontend interrompt son attente après 120 secondes, sans annuler un traitement déjà commencé sur le serveur. La reprise reste possible ; une file de traitement et des limites CPU/mémoire sont à prévoir avant une ouverture publique.
- `app/embeddings.py` fournit un adaptateur local FastEmbed, configuré par `FASTEMBED_MODEL`. Le modèle initial est multilingue et produit des vecteurs de 384 dimensions ; il est téléchargé au premier lancement puis exécuté localement, sans clé ni facturation par requête.
- Le fournisseur du LLM de génération reste à choisir et est indépendant du provider d'embeddings.
- Les embeddings ne sont pas encore persistés ni utilisés pour le retrieval. Ne pas activer la lecture anonyme Supabase pour des documents étudiants.

## Organisation par fonctionnalité
- `app/extraction/` : parseurs, découpage, sécurité des archives et récupération des extractions.
- `app/upload/` : orchestration des documents privés et routes associées.
- `app/main.py` assemble les routes ; ajouter les prochaines fonctionnalités dans leur package plutôt qu'à la racine de `app`.
- Les modules historiques seront déplacés lorsque leur fonctionnalité sera retravaillée. Les parseurs OCR et Office hérités restent séparés, sans supposer que tous les formats ont des pages.

## Vérification de l'extraction
- Depuis `backend`, lancer `.\.venv\Scripts\python.exe -m pytest -q`.
- Les tests synthétiques couvrent OCR d'images/PDF (et un échantillon réel local), conversion DOC/PPT simulée, tableaux DOCX/PPTX, spine EPUB, localisateurs, dispatch et paquets invalides. Appliquer `sql/course_document_ocr_legacy.sql` après `course_document_locations.sql` pour étendre les formats acceptés en base et dans le bucket privé.
- `tests/course_extraction.sql` teste les transactions, la RLS entre deux comptes, les privilèges anonymes, les liens aux projets et la suppression en cascade. L'exécuter avec `psql -v ON_ERROR_STOP=1 -f tests/course_extraction.sql` sur une base de test où les schémas Auth/Storage et les migrations sont installés ; les données de test sont annulées par `rollback`.
- Parcours navigateur validé avec un compte dédié : upload automatique, PDF multipage, erreur PDF invalide, image stockée sans extraction, reprise, rechargement, association au projet et recherche avec provenance.

## Contrats v1
- metadata: app/schemas.py -> ChunkMetadata
- sortie assistant: app/schemas.py -> AssistantResponse
