# PNLP Web Application

Ce projet est une application web pour le Programme National de Lutte contre le Paludisme (PNLP) du Sénégal, développée avec Angular.

## Aperçu

L'application PNLP est conçue pour fournir des informations sur les programmes de lutte contre le paludisme au Sénégal, présenter des statistiques sur la prévalence du paludisme, et offrir des ressources éducatives et des documents importants.

## Fonctionnalités

- **Page d'accueil** : Présentation du PNLP, statistiques clés, actualités et partenaires
- **À propos** : Informations sur la mission, les objectifs, l'équipe et l'historique du PNLP
- **Statistiques** : Visualisations interactives des données sur le paludisme au Sénégal
- **Ressources** : Documents, guides et ressources éducatives téléchargeables
- **Contact** : Formulaire de contact et informations de contact du PNLP

## Technologies utilisées

- Angular 17+
- TypeScript
- Bootstrap 5
- Chart.js pour les visualisations de données
- Bootstrap Icons
- Google Maps pour l'intégration de cartes

## Prérequis

- Node.js (v18 ou supérieur)
- npm (v9 ou supérieur)
- Angular CLI (v17 ou supérieur)

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/CodeWithSouleymane/pnlp_webapp.git
   ```

2. Accédez au répertoire du projet :
   ```bash
   cd pnlp_webapp/pnlp-app
   ```

3. Installez les dépendances :
   ```bash
   npm install
   ```

4. Lancez le serveur de développement :
   ```bash
   ng serve
   ```

5. Ouvrez votre navigateur et accédez à `http://localhost:4200/`

## Structure du projet

```
pnlp-app/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── home/
│   │   │   ├── about/
│   │   │   ├── statistics/
│   │   │   ├── resources/
│   │   │   └── contact/
│   │   ├── app.component.ts
│   │   ├── app.component.html
│   │   ├── app.component.scss
│   │   └── app.routes.ts
│   ├── assets/
│   │   ├── images/
│   │   └── data/
│   ├── styles.scss
│   └── index.html
├── angular.json
├── package.json
└── tsconfig.json
```

## Déploiement

Pour créer une version de production de l'application :

```bash
ng build --configuration production
```

Les fichiers de build seront stockés dans le répertoire `dist/`.

## Contribution

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion concernant ce projet, veuillez contacter :
- Email : contact@pnlp.sn
- Site web : www.pnlp.sn
