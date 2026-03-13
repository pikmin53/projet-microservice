import bdd_pytorch_service.metrics as mp
import bdd_tensorflow_service.metrics as mt
import bdd_log.bdd_log as log
import log_service


from fastapi import FastAPI

app = FastAPI()

# exécution de la création des tables et démarrage des consummer kafka
@app.on_event("startup")
def sartup():
    # création des tables
    log.init_db()
    mp.init_db()
    mt.init_db()
    #strat des consummer kafka
    log.start_consumer()
    mp.start_consumer()
    mt.start_consumer()

    log_service.log_event("BDD-service", "INFO", "Tables ajoutees et connexion avec kafka réussie")


@app.get("/")
async def root():
    return {"message": "Hello World"}