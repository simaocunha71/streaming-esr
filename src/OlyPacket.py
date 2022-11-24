# Packet de comunicação de rede overlay (a definir ainda)
import pickle
class OlyPacket:

    def __init__(self):
        pass

    # Ligação (Nodo->Bootstrapper)
    # Resposta da ligação (Bootstrapper->Nodo)(vizinhos)
    # Proba (Nodo->Nodo,Nodo->Servidor) (timestamp,nº saltos)

    def encode(self,flag,payload):
        self.flag = flag
        self.payload = payload
        return pickle.dumps(self)

    def decode(self,bytearray):
        self = pickle.loads(bytearray)
        return self
