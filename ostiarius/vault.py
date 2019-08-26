from hvac import Client
from sanic.log import logger

from ostiarius.const import GITHUB_TOKEN, RUN_ENV


class VaultClient:
    _vault: Client = None

    @classmethod
    def init(cls):
        if GITHUB_TOKEN and not cls._vault:
            cls._vault = Client("https://vault.entrydsm.hs.kr")
            cls._vault.auth.github.login(token=GITHUB_TOKEN)

            logger.info("Vault: initialized") \
                if cls._vault.is_authenticated() \
                else logger.error("Vault: not authenticated")

        else:
            logger.error("Vault: failed to initialize")

    @property
    def jwt_secret_key(self):
        return self._vault.read(f"/service-secret/{RUN_ENV}/jwt-key")["data"]["key"]


class Setting:
    _vault_client: VaultClient = None

    def __init__(self, vault_client: VaultClient):
        self._vault_client = vault_client

    @property
    def jwt_secret_key(self):
        return self._vault_client.jwt_secret_key


settings = Setting(VaultClient())
