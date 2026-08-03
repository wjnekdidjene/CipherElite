CipherElite = None


def init_client(client_instance):
    global CipherElite
    CipherElite = client_instance


def get_client():
    global CipherElite
    return CipherElite