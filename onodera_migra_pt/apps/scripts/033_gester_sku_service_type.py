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
    SkuServiceType,
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
url = 'http://onoderapt.swerp.com.br/api/lista/TipoServico'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
tipos_servico_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(tipos_servico_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for tipo_servico_json in tipos_servico_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    with transaction.atomic(using="gester"):
        sku_service_type_id = leTraducaoId(
            "tipo_servico", tipo_servico_json["id"], "sku_service_type"
        )
        sku_service_type = SkuServiceType.objects.filter(id=sku_service_type_id).first()

        if sku_service_type is None:
            sku_service_type = SkuServiceType.objects.filter(
                name=tipo_servico_json["descricao"]
            ).first()

        if sku_service_type is None:
            acao = "criado"
        else:
            acao = "atualizado"

        if sku_service_type is None or parametros.update_if_exists:
            ### ATRIBUI OS VALORES PARA 'SkuServiceType' ###
            if not sku_service_type:
                sku_service_type = SkuServiceType()
                sku_service_type.created_by_id = 1
                sku_service_type.last_edit_by_id = 1
                sku_service_type.created_on = datetime.now().astimezone()
                sku_service_type.last_edit_on = datetime.now().astimezone()
                sku_service_type.is_active = True
                sku_service_type.is_template = False
                sku_service_type.corporate_group_id = parametros.corporate_group_id
                sku_service_type.name = tipo_servico_json["descricao"][:30]
                sku_service_type.save()

            if sku_service_type_id is None:
                criaTraducaoId(
                    "tipo_servico",
                    tipo_servico_json["id"],
                    "sku_service_type",
                    sku_service_type.id,
                )
            elif sku_service_type_id != sku_service_type.id:
                atualizaTraducaoId(
                    "tipo_servico",
                    tipo_servico_json["id"],
                    "sku_service_type",
                    sku_service_type.id,
                )

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
