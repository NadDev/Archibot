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
python -m uvicorn app.main:app --reload

Note:
- Si vous installez hors venv, Windows peut afficher des warnings "script not on PATH".
- Le mode venv evite les conflits de dependances avec les packages globaux.

## Configuration Supabase (D1)
Le backend utilise Supabase si les variables suivantes sont definies dans .env:
- SUPABASE_URL
- SUPABASE_PUBLISHABLE_KEY (utiliser une cle API compatible supabase-py, typiquement anon)
- ARCHIBOT_CHUNKS_TABLE (optionnel, defaut: chunks)

Sans ces variables (ou si la cle n'est pas compatible), le backend reste utilisable avec des donnees de demo en memoire.

### Schema minimal table chunks
La table cible doit contenir au minimum:
- text (text)
- source_type (text): course | general | local_regulation
- source_id (text)
- project_id (text)
- doc_version (text)
- locality (text, nullable)
- ingested_at (timestamptz)

Exemple SQL:

create table if not exists chunks (
   id bigserial primary key,
   text text not null,
   source_type text not null,
   source_id text not null,
   project_id text not null,
   doc_version text not null,
   locality text,
   ingested_at timestamptz not null default now()
);

## Endpoints initiaux
- GET /health
- GET /v1/demo-response
- POST /v1/retrieval/search
- POST /v1/assistant/answer

## Contrats v1
- metadata: app/schemas.py -> ChunkMetadata
- sortie assistant: app/schemas.py -> AssistantResponse
