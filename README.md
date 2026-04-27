Creer un environement 
python -m venv venv
venv\Scripts\activate
 installer les package 
 pip install pymongo polars
 creer le fichier requirement 
 pip freeze > requirements.txt
 Ce fichier liste toutes les versions exactes des packages installés.

Utile si tu veux partager ton projet ou le réinstaller ailleurs 
puis installer pip install -r requirements.txt"# Concevez-analyser" 

Exécuter un script dans le dossier dossier taper la commande suivante 
```bash
python -m Script.le nom du fichier
```

#### Preapre RéplicaSet
##### Création Dossier  
```bash
mkdir mongo/rs1
mkdir mongo/rs2
mkdir mongo/arb
```
Chaque dossier représente un serveur MongoDB

*Important* Verifier si MongoDb tourne
MongoDB installé via *MSI* démarre souvent automatiquement et bloque le port 27017 empêchant le ReplicaSet de fonctionner 
desactiver entant que admin
*Vérifier le service*
```bash
Get-Service | Where-Object {$_.Name -like "*Mongo*"}
```
*Si un service MongoDB apparaît, l’arrêter :*
```bash
Stop-Service MongoDB
```
*Le désactiver pour éviter qu’il redémarre :*
```bash
Set-Service MongoDB -StartupType Disabled
```
*Vérifier que le port 27017 est libre :*
```bash
netstat -ano | findstr 27017
```
*Réactivé le service*
```bash
Set-Service MongoDB -StartupType Automatic

```
```bash
Start-Service MongoDB

```
```bash
Get-Service MongoDB

```
###### Lancement ReplicaSet
Ouvert trois cmd cote a cote 
*Fenêtre 1 — PRIMARY (port 27017)*
```bash
mongod --replSet rs0 --port 27017 --dbpath mongo/rs1 --bind_ip localhost
```
*Fenêtre 2 — SECONDARY (port 27018)*
```bash
mongod --replSet rs0 --port 27018 --dbpath mongo/rs2 --bind_ip localhost
```
*Fenêtre 3 — ARBITRE (port 27019)*
```bash
mongod --replSet rs0 --port 27019 --dbpath mongo/arb --bind_ip localhost
```
de laisser les trois cmd ouvert 
###### Initialiser le ReplicaSet
Ouvrir un qautrieme fenetre 
```bash
mongosh --port 27017
```
puis d'exécuter
```bash
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },
    { _id: 1, host: "localhost:27018" },
    { _id: 2, host: "localhost:27019", arbiterOnly: true }
  ]
})
```
Si message "ok" : 1 tous fonctionne bien 
###### Vérifier le statut du ReplicaSet
```bash
rs.status()
```
on doit voir 

    -PRIMARY = 2707
    -SECONDARY = 27018
    -ARBITER = 27019

###### Tester la réplication
ouvert deux terminal un pour 27017 et l'autre pour 27018
```bash
mongosh --port 27017
```
on doit voir dans le code "rs0 [direct: primary] test>" on peut alors taper la commande suivante 

```bash
use Jeuxolympique2024
db.test.insertOne({ ville: "Paris", ok: true })
``` ```
et dans le second 
```bash
mongosh --port 27018
```
on doit voir se code 
```bash
use Jeuxolympique2024

db.getMongo().setReadPref("secondary")
db.test.find()
```
__
*Notes importantes*
Les trois fenêtres mongod doivent rester ouvertes pendant toute la durée du test.

Si tu vois l’erreur “This node was not started with replication enabled”, cela signifie que le port 27017 était occupé par le service MongoDB Windows.

Toujours vérifier que le port 27017 est libre avant de lancer le PRIMARY.
__
#### Sharding 
##### Creation de l’arborescence
```bash
mkdir mongo/config
mkdir mongo/shard1
mkdir mongo/shard2
mkdir mongo/mongos
```
###### Lancement des serveur et connexion 
Pour tous les serveur et connextion s'assuré que chacun se trouve dans un terminal et de laisser le terminal tournée pour le bon déroulement 

*Important* Comme pour les replicaset s'assurer que les serveur son libres dans se cas stopper les pour le déroulement 
 
 Voci les commande pour lancer les serveur et la connexion a se serveur 
```bash
mongod --configsvr --replSet configReplSet --port 27019 --dbpath ./config
```
```bash
mongosh --port 27019
```
shard1
```bash
mongod --shardsvr --replSet shardParis --port 27018 --dbpath ./shard1
```
```bash
mongosh --port 27018
```
shard2
```bash
mongod --shardsvr --replSet shardLyon --port 27020 --dbpath ./shard2
```
```bash
mongosh --port 27020
```
la router mongos
```bash
mongos --configdb configReplSet/localhost:27019 --port 27017
```
```bash
mongosh --port 27017
```
###### Initiate
Une fois les serveur lancer et que tous est connecter de initialiser la partie config et les shard 
Config
```bash
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [
    { _id: 0, host: "localhost:27019" }
  ]
})
```
une fois initiate effectué de lancer la comme 
```bash 
rs.status()
```
pour faire la verification 
shard1
```bash
rs.initiate({
  _id: "shardParis",
  members: [
    { _id: 0, host: "localhost:27018" }
  ]
})
```
shard2
```bash
rs.initiate({
  _id: "shardLyon",
  members: [
    { _id: 0, host: "localhost:27020" }
  ]
})
```
###### Ajout Shards au cluster
pour la partie routeur  une fois connecter on ajouter les  shards au clusters
```bash
sh.addShard("shardParis/localhost:27018")
sh.addShard("shardLyon/localhost:27020")
```
et de verifier avec la commande 
```bash
sh.status()
```
une fois les shards ajouter au cluster on dois les activés sur la base ("JeuxOlympique2024") 
```bash
sh.enableSharding("JeuxOlympique2024")
```

```bash
sh.shardCollection("maBase.clients", { ville: 1 })
```
et tester pour voir si tous fonctionne bien 
```bash
use JeuxOlympique2024

db.clients.insertMany([
  { nom: "Durand", ville: "Paris" },
  { nom: "Martin", ville: "Paris" },
  { nom: "Dupont", ville: "Lyon" },
  { nom: "Morel", ville: "Lyon" }
])
```
Vérifier la répartition des chunks
```bash
sh.status()
```
Vérifier que les documents sont bien routés
```bash
db.clients.find({ ville: "Paris" }).explain("executionStats")
```
la même chose pour la ville Lyon
```bash
db.clients.find({ ville: "Lyon" }).explain("executionStats")
```

```bash
```
```bash
```


mongod --replSet rs0 --port 27017 --dbpath mongo/rs1 --bind_ip localhost

mongod --replSet rs0 --port 27018 --dbpath mongo/rs2 --bind_ip localhost

mongod --replSet rs0 --port 27019 --dbpath mongo/arb --bind_ip localhost
