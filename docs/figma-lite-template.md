# Figma Lite Template (MVP)

## Objectif
Disposer d'un cadre UX/UI utile sans surconsommation de temps, tokens ou budget.

## Principe
- 1 flow principal
- 3 ecrans critiques
- 1 mini design kit
- 1 prototype cliquable

## Structure conseillee du fichier Figma

### Page 1: Flow
- Frame `FLOW-001 Question -> Reponse -> Action`
- Frame `FLOW-002 Upload -> Ingestion -> Statut`
- Frame `FLOW-003 Exercice -> Correction -> Progression`

### Page 2: Ecrans MVP
- Frame `SCR-CHAT-001 Chat pedagogique`
- Frame `SCR-LIB-001 Bibliotheque documentaire`
- Frame `SCR-EXO-001 Exercices et correction`

Pour chaque ecran, inclure:
- etat normal
- etat loading
- etat erreur
- etat sans source

### Page 3: Mini Design Kit
- couleurs semantiques (success/warning/error/info)
- typo (H1, H2, body, caption)
- boutons (primary, secondary, disabled)
- cartes de contenu
- tags provenance: cours / regle generale / source locale

### Page 4: Prototype
- parcours cliquable desktop
- parcours cliquable mobile
- interactions minimales (navigation + etats critiques)

## Nommage standard
- `FLOW-xxx` pour les parcours
- `SCR-xxx` pour les ecrans
- `CMP-xxx` pour composants
- `VAR-xxx` pour variantes

## Checklist de completion (definition of done UX)
- [ ] 3 ecrans MVP finalises
- [ ] 4 etats UX critiques par ecran
- [ ] tags provenance visibles dans l'ecran chat
- [ ] prototype cliquable desktop + mobile
- [ ] revue PM/PO faite
- [ ] revue Dev faite (faisabilite)

## Timebox recommande
- Setup fichier: 30 min
- Wireframes: 2h
- UI propre MVP: 3h
- Prototype + revue: 1h30

Total: environ 1 jour de travail UX concentre.

## Anti-overkill (a eviter au stade MVP)
- design system exhaustif
- animations complexes
- variantes pour tous les edge cases
- pixel perfection avant validation produit

## Livrables minimum a joindre aux tickets
- lien frame flow
- lien frame ecran concerne
- captures etats critiques
- note de decisions UX