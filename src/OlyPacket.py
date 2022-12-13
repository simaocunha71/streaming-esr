# Packet de comunicação de rede overlay (a definir ainda)
import pickle

"""
OlyPacket implementa mensagens de controlo da rede overlay. As mensagens são em formato string, e os seus campos
são de parados por ';'. Um Olypacket tem um tamanho fixo de 250 bytes.

TYPE:
    H -> Hello packet, pacote de registo no bootstrapper
    HR -> Hello response, pacote de resposta ao Hello
    P -> Probe packet, pacote de proba
    SETUP -> Setup packet
    PLAY -> Play packet
    PAUSE -> Pause packet
    TEARDOWN -> Teardown packet
PAYLOAD:
    O payload só terá valores quando o TYPE for HR ou P. O PAYLOAD tem os seus valores separados
pelo caracter ",".

"""

class OlyPacket:

    def __init__(self):
        pass

    def encode(self,type,payload):
        data = flag + ";"

        if payload:
            # O payload tem que ser sempre uma lista
            for value in payload:
                data += value + ","

            # Tira a virgula em excesso e acrescentar último separador
            data = data[:-1] + ";"
        else:
            # Se o payload for vazio
            data += ";"
        # Adiciona padding até atingir o tamanho de 250
        data.ljust(250,"0")
        return data.encode("utf-8")

    def decode(self,bytearray):
        data = bytearray.decode("utf-8")
        data_fields = data.split(";")

        # Tipo o pacote
        self.type = data_fields[0]
        # Array com os valores o payload
        self.payload = data_fields[1].slit(",")

        return self
