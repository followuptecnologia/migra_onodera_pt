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
    CrmMediaGroup,
    CrmMedia,
    CrmMediaUnity,
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
data = {"descricaoMedia": " "}
url = 'http://onoderapt.swerp.com.br/api/midia'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
midias_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(midias_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for midia_json in midias_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    with transaction.atomic(using="gester"):
        crm_media_group_id = leTraducaoId(
            "origem_cadastro", midia_json["idOrigem"], "crm_media_group"
        )
        crm_media_group = CrmMediaGroup.objects.filter(id=crm_media_group_id).first()

        if not crm_media_group:
            crm_media_group = CrmMediaGroup.objects.filter(name=midia_json["origem"]).first()

        if not crm_media_group:
            crm_media_group = CrmMediaGroup()
            crm_media_group.is_active = True
            crm_media_group.is_template = False
            crm_media_group.name = midia_json["origem"]
            crm_media_group.corporate_group_id = parametros.corporate_group_id
            crm_media_group.created_by_id = 1
            crm_media_group.created_on = datetime.now().astimezone()
            crm_media_group.save()
            print(f"CrmMediaGroup {crm_media_group.name} {acao}")

            criaTraducaoId(
                "origem_cadastro",
                midia_json["idOrigem"],
                "crm_media_group",
                crm_media_group.id,
            )
        else:
            atualizaTraducaoId(
                "origem_cadastro",
                midia_json["idOrigem"],
                "crm_media_group",
                crm_media_group.id,
            )

        crm_media_id = leTraducaoId(
                "origem_media",
                midia_json["id"],
                "crm_media",
                corporate_group_unity.id,
            )
        crm_media = CrmMedia.objects.filter(id=crm_media_id).first()

        if crm_media_id is None:
            acao = "criado"
        else:
            acao = "atualizado"

        if crm_media is None or parametros.update_if_exists:
            # ATRIBUI OS VALORES PARA 'Medias' #
            if crm_media is None:
                crm_media = CrmMedia()
                crm_media.is_template = False
                crm_media.is_active = midia_json["ativo"]
                crm_media.name = midia_json["nome"]
                crm_media.description = midia_json["descricaoMedia"]
                crm_media.corporate_group_id = parametros.corporate_group_id
                crm_media.corporate_group_unity_id = None
                crm_media.created_by_id = 1
                crm_media.created_on = datetime.now().astimezone()
                crm_media.media_group_id = crm_media_group.id
                crm_media.save()

                if crm_media_id is None:
                    criaTraducaoId(
                        "origem_media",
                        midia_json["id"],
                        "crm_media",
                        crm_media.id,
                        corporate_group_unity.id,
                    )
                elif crm_media_id != crm_media.id:
                    atualizaTraducaoId(
                        "origem_media",
                        midia_json["id"],
                        "crm_media",
                        crm_media.id,
                        corporate_group_unity.id,
                    )

            media_unity = CrmMediaUnity.objects.filter(
                media_id=crm_media.id,
                corporate_group_unity_id=corporate_group_unity.id,
            ).first()
            if not media_unity:
                media_unity = CrmMediaUnity()
                media_unity.created_on = datetime.now().astimezone()
                media_unity.created_by_id = 1
                media_unity.last_edit_on = datetime.now().astimezone()
                media_unity.last_edit_by_id = 1
                media_unity.is_active = True
                media_unity.is_template = False
                media_unity.corporate_group_id = parametros.corporate_group_id
                media_unity.media_id = crm_media.id
                media_unity.corporate_group_unity_id = corporate_group_unity.id
                media_unity.save()
