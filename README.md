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

#### Preapre RéplicaSet
##### Création Dossier  
```bash
mkdir mongo/rs1
mkdir mongo/rs2
mkdir mongo/arb
```
Chaque dossier représente un serveur MongoDB

#### *Important* Verifier si MongoDb tourne
MongoDB installé via *MSI* démarre souvent automatiquement et bloque le port 27017 empêchant le ReplicaSet de fonctionner 

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
##### Lancement ReplicaSet
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
##### Initialiser le ReplicaSet
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
##### Vérifier le statut du ReplicaSet
```bash
rs.status()
```
on doit voir 

    -PRIMARY = 2707
    -SECONDARY = 27018
    -ARBITER = 27019

##### Tester la réplication
ouvert deux terminal un pour 27017 et l'autre pour 27018
```bash
mongosh --port 27017
```
on doit voir dans le code "rs0 [direct: primary] test>" on peut alors taper la commande suivante 

```bash
use Jeuxolympique2024
db.test.insertOne({ ville: "Paris", ok: true })
``` 
et dans le second 
```bash
mongosh --port 27018
```
on doit voir se code 
```bash
rs.slaveOk()
db.test.find()
```
__
*Notes importantes*
Les trois fenêtres mongod doivent rester ouvertes pendant toute la durée du test.

Si tu vois l’erreur “This node was not started with replication enabled”, cela signifie que le port 27017 était occupé par le service MongoDB Windows.

Toujours vérifier que le port 27017 est libre avant de lancer le PRIMARY.
__
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```
```bash
```


mongod --replSet rs0 --port 27017 --dbpath mongo/rs1 --bind_ip localhost

mongod --replSet rs0 --port 27018 --dbpath mongo/rs2 --bind_ip localhost

mongod --replSet rs0 --port 27019 --dbpath mongo/arb --bind_ip localhost
