from locust import HttpUser, task, between, constant_throughput
import random


TAMANHO_POOL = 500

POOL_CEPS = [f"{random.randint(1001000, 99999999):08d}" for _ in range(TAMANHO_POOL)]

class TesteApiCep(HttpUser):
    wait_time = between(0.1, 0.5)
    # wait_time = constant_throughput(0.1)

    @task
    def buscar_cep(self):
        cep_sorteado = random.choice(POOL_CEPS)
        
        self.client.get(
            f"/cep/{cep_sorteado}", 
            headers={'accept': 'application/json'},
            name="/cep/[cep]"
        )