# Note de Conformité RGPD – Base de Données Client

1. Objectif

Cette note explique les choix de conception de la base de données relative aux clients et aux données personnelles simulées, afin de garantir la conformité au Règlement Général sur la Protection des Données (RGPD).

2. Pseudonymisation

Les informations personnellement identifiables (PII) telles que login et mot_de_passe sont pseudonymisées :

login est stocké sous forme de chaîne unique générée aléatoirement via Faker pour les données simulées.

mot_de_passe est haché avec un algorithme sécurisé (Argon2) afin d’empêcher toute identification directe.

Cette approche réduit le risque de ré-identification tout en permettant des tests fonctionnels et analytiques.

3. Rétention et suppression des données

Chaque enregistrement dispose d’un champ date_suppression : lorsqu’une suppression est requise, la date est renseignée et les données sont anonymisées (anonymise=True) plutôt que simplement supprimées.

Les champs date_creation et date_derniere_utilisation permettent :

de tracer l’activité des comptes,

de définir des politiques de rétention automatique, par exemple la suppression ou l’anonymisation après un certain délai d’inactivité.

La cascade "all, delete-orphan" sur la relation donnees garantit qu’en cas de suppression d’un client, ses données personnelles associées sont également supprimées ou anonymisées.

4. Minimisation et sécurité des données

Seules les données strictement nécessaires à l’usage simulé sont collectées.

Les mots de passe ne sont jamais stockés en clair.

Les informations d’âge et de région sont stockées sous forme d’identifiants (age_id, region_id) permettant des analyses statistiques sans exposition directe des informations personnelles.

5. Conformité RGPD

Principe de minimisation : seules les informations nécessaires à l’exercice des fonctions simulées sont conservées.

Principe de pseudonymisation et sécurité : hachage des mots de passe et génération de logins aléatoires.

Principe de limitation de conservation : les dates de création, de dernière utilisation et de suppression permettent la mise en œuvre de politiques de rétention conformes.

Traçabilité et auditabilité : toute modification ou suppression des données est consignée par les champs dédiés et peut être étendue avec un système de journalisation (logging).