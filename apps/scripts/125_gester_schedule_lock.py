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
    atualizaTraducaoId, ifNone
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    Resource,
    ScheduleLock, ScheduleLockResource,
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
data = {"nome": ""}
url = 'http://onoderapt.swerp.com.br/api/colunas'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
colunas_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(colunas_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for coluna_json in colunas_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/colunas/" + str(coluna_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_coluna_json = response.json()

            resource_id = leTraducaoId(
                "consultor", response_coluna_json["id"], "resource", corporate_group_unity.id
            )
            resource = Resource.objects.filter(id=resource_id).first()

            if resource is not None and response_coluna_json["excecoes"]:
                for excecao in response_coluna_json["excecoes"]:
                    schedule_lock_id = leTraducaoId(
                        "consultor_horario", excecao["id"], "schedule_lock"
                    )
                    schedule_lock = ScheduleLock.objects.filter(id=schedule_lock_id).first()

                    if not schedule_lock:
                        acao = colored("criado", "green")
                    else:
                        acao = "atualizado"

                    if not schedule_lock or parametros.update_if_exists:
                        if not schedule_lock:
                            schedule_lock = ScheduleLock()
                            acao = colored("criado", "green")
                        else:
                            acao = "atualizado"

                        schedule_lock.created_on = datetime.now().astimezone()
                        schedule_lock.last_edit_on = datetime.now().astimezone()
                        schedule_lock.created_by_id = 1
                        schedule_lock.last_edit_by_id = 1
                        schedule_lock.corporate_group_id = parametros.corporate_group_id
                        schedule_lock.corporate_group_unity_id = parametros.codigo_gester
                        schedule_lock.is_active = True
                        schedule_lock.is_template = False
                        schedule_lock.reason = str(
                            ifNone(excecao["descricao"], "")
                        ).upper()
                        schedule_lock.begin_time = excecao["data"]
                        schedule_lock.end_time = (
                            excecao["dataFim"]
                            if excecao["data"] <= excecao["dataFim"]
                            else excecao["data"]
                        )

                        if "FERIADO" in schedule_lock.reason:
                            schedule_lock.block_type = "holiday"
                        elif "HORÁRIO ESPECIAL" in schedule_lock.reason:
                            schedule_lock.block_type = "special_time"
                        else:
                            schedule_lock.block_type = "working_range"

                        schedule_lock.save()

                        if schedule_lock_id is None:
                            criaTraducaoId(
                                "consultor_horario",
                                excecao["id"],
                                "schedule_lock",
                                schedule_lock.id,
                            )
                        else:
                            atualizaTraducaoId(
                                "consultor_horario",
                                excecao["id"],
                                "schedule_lock",
                                schedule_lock.id,
                            )

                    # SCHEDULE_LOCK_RESOURCE
                    schedule_lock_resource_id = leTraducaoId(
                        "consultor_horario", excecao["id"], "schedule_lock_resource"
                    )
                    schedule_lock_resource = ScheduleLockResource.objects.filter(
                        id=schedule_lock_resource_id
                    ).first()

                    if not schedule_lock_resource:
                        acao = colored("criado", "green")
                    else:
                        acao = "atualizado"

                    if not schedule_lock_resource or parametros.update_if_exists:
                        if not schedule_lock_resource:
                            schedule_lock_resource = ScheduleLockResource()

                        schedule_lock_resource.created_on = datetime.now().astimezone()
                        schedule_lock_resource.last_edit_on = datetime.now().astimezone()
                        schedule_lock_resource.created_by_id = 1
                        schedule_lock_resource.last_edit_by_id = 1
                        schedule_lock_resource.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        schedule_lock_resource.corporate_group_unity_id = parametros.codigo_gester
                        schedule_lock_resource.is_active = True
                        schedule_lock_resource.is_template = False
                        schedule_lock_resource.schedule_lock_id = schedule_lock.id
                        schedule_lock_resource.resource_id = resource.id

                        schedule_lock_resource.save()

                        if not schedule_lock_resource_id:
                            criaTraducaoId(
                                "consultor_horario",
                                resource["id"],
                                "schedule_lock_resource",
                                schedule_lock_resource.id,
                            )
                        else:
                            atualizaTraducaoId(
                                "consultor_horario",
                                resource["id"],
                                "schedule_lock_resource",
                                schedule_lock_resource.id,
                            )

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
