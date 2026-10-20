# Calendar Share

[English](README.md) · **Français**

**Partagez n'importe quel calendrier Home Assistant avec votre téléphone, votre famille ou vos collègues grâce à un simple lien.**

Calendar Share transforme un calendrier de Home Assistant (école, travail, ramassage des déchets, club de sport, un calendrier Google ou CalDAV déjà ajouté…) en lien web privé. Collez ce lien dans Apple Calendrier, Google Agenda, Outlook ou toute application capable de « s'abonner à un calendrier » : les événements y apparaissent et se mettent à jour tout seuls.

## Pourquoi l'utiliser ?

Home Assistant sait afficher vos calendriers, mais les autres applications ne peuvent pas les lire : son API exige un en-tête d'authentification que les applications de calendrier ne savent pas envoyer. Calendar Share contourne ce problème en donnant à chaque calendrier son propre **long lien secret** (un « jeton » dans l'URL) à la place d'un identifiant. Toute personne qui possède le lien peut lire ce calendrier, et personne d'autre.

## Ce que vous obtenez

- **Un lien par calendrier.** `https://<votre-home-assistant>/api/calendar_share/<secret>`
- **Autant de liens que voulu**, tous indépendants : un par enfant, par calendrier, par personne… Chacun peut être régénéré ou supprimé sans toucher aux autres.
- **Lecture seule.** Le lien ne peut qu'afficher des événements. Il ne peut jamais rien créer, modifier ou supprimer.
- **Un capteur d'état** par lien, indiquant la dernière consultation et le nombre d'événements partagés.
- **Vous choisissez ce qui est partagé** : tout le calendrier, ou seulement une période (par ex. le dernier mois et les trois prochains).

## ⚠️ Important : utilisez HTTPS

Le secret est contenu dans le lien. En HTTP simple, n'importe qui sur le trajet réseau peut le lire. N'utilisez cette intégration que si votre Home Assistant est accessible en **HTTPS** (Nabu Casa Cloud, ou votre propre reverse proxy avec un certificat valide).

Traitez le lien comme un mot de passe : quiconque l'a peut voir le calendrier. S'il fuite, régénérez-le (voir plus bas).

## Installation

### Avec HACS (recommandé)

1. Dans HACS, recherchez **Calendar Share** puis cliquez sur **Télécharger**.
2. Redémarrez Home Assistant.

S'il n'apparaît pas encore, ajoutez-le comme dépôt personnalisé : menu ⋮ → **Dépôts personnalisés**, collez l'URL de ce dépôt et choisissez la catégorie **Intégration**.

### Manuellement

Copiez le dossier `custom_components/calendar_share` dans le dossier `custom_components` de votre configuration Home Assistant, puis redémarrez.

## Configuration

1. Allez dans **Paramètres → Appareils et services → Ajouter une intégration** et choisissez **Calendar Share**.
2. Sélectionnez le calendrier à partager.
3. Votre lien s'affiche **une seule fois**. Copiez-le immédiatement.
4. Abonnez-vous-y dans votre application de calendrier :
   - **iPhone / iPad :** Réglages → Calendrier → Comptes → Ajouter un compte → Autre → Ajouter un calendrier avec abonnement.
   - **Google Agenda (sur ordinateur) :** Autres agendas (+) → À partir de l'URL. Il apparaît ensuite aussi sur votre téléphone Android.
   - **Outlook :** Ajouter un calendrier → S'abonner à partir du web.
   - **Toute autre application :** cherchez « s'abonner à un calendrier » ou « ajouter un calendrier par URL ».

Les applications actualisent les calendriers auxquels on s'abonne à leur rythme (de quelques minutes à plusieurs heures) : un nouvel événement peut donc mettre du temps à apparaître.

## Options

Modifiables à tout moment avec le bouton **Configurer** de l'intégration.

| Option | Effet |
| --- | --- |
| **Calendrier complet** | Partage tout le contenu du calendrier, passé et futur. Les deux réglages suivants sont alors ignorés. |
| **Jours à venir** | Jusqu'où dans le futur les événements sont partagés (par défaut 400 jours, max 10 ans). |
| **Jours passés** | Jusqu'où dans le passé les événements sont partagés (par défaut 400 jours, max 10 ans). |
| **Régénérer le jeton** | Crée un nouveau lien et désactive aussitôt l'ancien. Le nouveau lien s'affiche une seule fois ; mettez ensuite vos abonnements à jour. |

La période par défaut (environ 13 mois de chaque côté) suffit à la plupart des calendriers, y compris scolaires : il est rarement nécessaire de la modifier.

## Sécurité

- Les liens sont générés automatiquement avec `secrets.token_urlsafe(32)`. Impossible d'en choisir un faible.
- Le secret est vérifié en temps constant et n'est jamais écrit dans les journaux de Home Assistant.
- Chaque lien est lié à un seul calendrier, choisi par vous. Il n'existe pas de lien « tout partager ».
- Régénérer ou supprimer un lien prend effet immédiatement et n'affecte pas les autres.
- Le lien est indépendant de vos comptes Home Assistant et de vos jetons d'accès longue durée.

## Dépannage

- **L'application indique un lien invalide / 403 :** le lien a été régénéré ou mal copié. Recopiez le lien actuel.
- **Des événements manquent :** vérifiez les options (jours passés / à venir, ou activez *Calendrier complet*), puis attendez l'actualisation de votre application.
- **Heures décalées :** le flux utilise le fuseau horaire défini dans Home Assistant (Paramètres → Système → Général).

## Développement

```bash
pip install -r requirements_test.txt
ruff check .
mypy --strict custom_components/calendar_share
pytest
```

## Licence

MIT, voir [LICENSE](LICENSE).
