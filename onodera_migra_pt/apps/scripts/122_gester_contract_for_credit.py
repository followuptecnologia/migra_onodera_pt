import json
import os
import sys

from termcolor import colored
import django
import jsonpath
import requests

PROJECT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.append(PROJECT_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings"

django.setup()


from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, Partner,
    PartnerUnityCustomer,
    LegacyTranslateId,
)

corporate_group_unity = CorporateGroupUnity.objects.filter(
    id=parametros.codigo_gester
).first()

if not corporate_group_unity:
    print(
        colored(
            f"A filial do sistema legado não possui uma unidade corporativa no Gester. "
            "grey",
            "on_red",
        )
    )
    exit(-1)

print(
    f"Unidade: {corporate_group_unity.abbreviated_name} - Id da unidade: {corporate_group_unity.id}"
)

### TOKEN ###
url = "http://onoderapt.swerp.com.br/token"
headers = {"content-type": "multipart/form-data"}
data = {
    "grant_type": "password",
    "username": f"{parametros.codigofilial_sw}|master",
    "password": "cdc2103",
    "unidadeid": "undefined",
}
response = requests.post(url=url, data=data, headers=headers)
access_token = jsonpath.jsonpath(response.json(), "access_token")[0]

# PERCORRE OS CLIENTES PARA LISTAR AS TROCAS POR CLIENTE #
customers = PartnerUnityCustomer.objects.filter(corporate_group_unity_id=corporate_group_unity.id)
quant_total = customers.count()
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for customer in customers:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    partner = Partner.objects.filter(id=customer.partner_id).first()

    pessoa_legacy = LegacyTranslateId.objects.filter(
        legacy_table="pessoa",
        gester_table="partner",
        gester_id=partner.id
    ).first()
    if not pessoa_legacy:
        continue

    # ACESSANDO A API #
    headers = {
        "authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }
    data = {"id": pessoa_legacy.legacy_id, "nomePessoa": partner.name}
    url = 'http://onoderapt.swerp.com.br/api/clientes/creditos'

    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    creditos_json = response.json()

    # PERCORRENDO TODOS OS CADASTROS DA LISTA #
    for credito_json in creditos_json["creditos"]:
        #   with transaction.atomic(using="gester"):
        print(credito_json)
