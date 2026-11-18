# Les données fictives

Un jeu reproductible de personnes fictives sur les formations publiques (étudiants, enseignants,
administratifs, stages, vœux de mobilité, absences), pour travailler sans données réelles.

```bash
python Learnagement.py fake-data --size small|medium|large --seed N
```

Le générateur est une commande du lanceur (`launcher/fake_data/`). Il écrit le jeu dans
`database/data/`, que MySQL lit à sa première initialisation, avec le jeu public de
`database/open-data/Polytech_Annecy_Chambery/`. Il est aussi proposé au premier lancement, hors
production. Les comptes de test : le [README](../../README.md).
