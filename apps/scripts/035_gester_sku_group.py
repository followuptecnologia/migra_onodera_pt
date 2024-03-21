import json
import os
import sys
from datetime import datetime

from django.db import transaction
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

from apps.functions import (
    leTraducaoId,
    criaTraducaoId,
    atualizaTraducaoId,
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    SkuGroup,
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

### ACESSANDO A API ###
headers = {
    "authorization": "Bearer " + access_token,
    "Content-Type": "application/json",
}
data = {"descricao": ""}
url = 'http://onoderapt.swerp.com.br/api/lista/TipoAgenda'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
tipos_agenda_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(tipos_agenda_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for tipo_agenda_json in tipos_agenda_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    with transaction.atomic(using="gester"):
        sku_group_id = leTraducaoId("tipo_agenda", tipo_agenda_json["id"], "sku_group")
        sku_group = SkuGroup.objects.filter(id=sku_group_id).first()
        if sku_group is None:
            sku_group = SkuGroup.objects.filter(name=tipo_agenda_json["descricao"]).first()

        if not sku_group:
            acao = "criado"
        else:
            acao = "atualizado"

        if sku_group is None or parametros.update_if_exists:
            if sku_group is None:
                sku_group = SkuGroup()
                sku_group.created_by_id = 1
                sku_group.created_on = datetime.now().astimezone()
                sku_group.is_active = True
                sku_group.is_template = False
                sku_group.name = tipo_agenda_json["descricao"]
                sku_group.type = "service"
                sku_group.abbreviated_name = tipo_agenda_json["descricao"][:8]
                sku_group.corporate_group_id = parametros.corporate_group_id
                sku_group.save()

            if sku_group_id is None:
                criaTraducaoId(
                    "tipo_agenda",
                    tipo_agenda_json["id"],
                    "sku_group",
                    sku_group.id,
                )
            elif sku_group_id != sku_group.id or sku_group is not None:
                atualizaTraducaoId(
                    "tipo_agenda",
                    tipo_agenda_json["id"],
                    "sku_group",
                    sku_group.id,
                )

            print(f"SkuGroup {sku_group.name} {acao}")

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
