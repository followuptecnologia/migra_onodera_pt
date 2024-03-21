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
    Sku, Resource, ResourceAvailableTime,
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
url = 'http://onoderapt.swerp.com.br/api/equipamentos'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
equipamentos_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(equipamentos_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for equipamento_json in equipamentos_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/equipamentos/" + str(equipamento_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_equipment_json = response.json()
            sku_id = leTraducaoId(
                "maquina_filial",
                equipamento_json["id"],
                "sku",
                corporate_group_unity.id,
            )
            sku = Sku.objects.filter(id=sku_id).first()
            sku_equipment_type_id = leTraducaoId(
                "maquina", response_equipment_json["idMaquina"], "sku_equipment_type"
            )

            if sku is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if sku is None or parametros.update_if_exists:
                ### CADASTRA O EQUIPAMENTO EM 'Sku' ###
                if not sku:
                    sku = Sku()
                    sku.is_active = True
                    sku.is_template = False
                    sku.is_equipment = True
                    sku.is_separate_session_allowed = False
                    sku.is_product = False
                    sku.name = response_equipment_json["nome"]
                    sku.corporate_group_id = parametros.corporate_group_id
                    sku.description = response_equipment_json["nome"]
                    sku.product_type = "sales_item"
                    sku.sales_price = 0
                    sku.assessment_service = False
                    sku.created_on = datetime.now()
                    sku.allow_single_sale = True
                    sku.allow_package_sale = True
                    sku.sku_equipment_type_id = sku_equipment_type_id
                    sku.need_sign = False
                    sku.allow_courtesy = False
                    sku.allow_demonstration = False
                    sku.allow_replacement = False
                    sku.allow_schedule_in_call_center = False
                    sku.save()

                    if sku_id is None:
                        criaTraducaoId(
                            "maquina_filial",
                            response_equipment_json["id"],
                            "sku",
                            sku.id,
                            corporate_group_unity.id,
                        )
                    elif sku_id != sku.id:
                        atualizaTraducaoId(
                            "maquina_filial",
                            response_equipment_json["id"],
                            "sku",
                            sku.id,
                            corporate_group_unity.id,
                        )

            resource_id = leTraducaoId(
                "maquina_filial",
                response_equipment_json["id"],
                "resource",
                corporate_group_unity.id,
            )
            resource = Resource.objects.filter(id=resource_id).first()

            if resource_id is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if resource is None:
                ### ATRIBUI OS VALORES PARA 'Resource' ###
                if not resource:
                    resource = Resource()
                    resource.created_on = datetime.now()
                    resource.is_active = True
                    resource.is_template = False
                    resource.name = response_equipment_json["nome"]
                    resource.serial_number = ""
                    resource.specific_control = ""
                    resource.is_consultant = False
                    resource.type = "equipment"
                    resource.has_schedule_control = True
                    resource.corporate_group_id = parametros.corporate_group_id
                    resource.corporate_group_unity_id = corporate_group_unity.id
                    resource.equipment_sku_id = sku.id
                    resource.partner_id = None
                    resource.save()

                    if resource_id is not None and resource_id != resource.id:
                        #  Existe tradução mas para um id incorreto: corrige
                        atualizaTraducaoId(
                            "maquina_filial",
                            response_equipment_json["id"],
                            "resource",
                            resource.id,
                            corporate_group_unity.id,
                        )
                    else:
                        #  Tradução não existe ainda: cria uma nova
                        criaTraducaoId(
                            "maquina_filial",
                            response_equipment_json["id"],
                            "resource",
                            resource.id,
                            corporate_group_unity.id,
                        )

            # Horários (disponibilidade) do equipamento

            for horarios in response_equipment_json["horarios"]:
                if horarios["isTrabalha"] is False:
                    continue

                resource_available_time_id = leTraducaoId(
                    "equipamento_horario_periodo",
                    horarios["id"],
                    "resource_available_time",
                )
                resource_available_time = ResourceAvailableTime.objects.filter(
                    id=resource_available_time_id
                ).first()

                if not resource_available_time:
                    acao = colored("criado", "green")
                else:
                    acao = "atualizado"

                if not resource_available_time or parametros.update_if_exists:
                    if not resource_available_time:
                        resource_available_time = ResourceAvailableTime()
                        resource_available_time.created_on = datetime.now().astimezone()
                        resource_available_time.created_by_id = 1
                        resource_available_time.last_edit_on = datetime.now().astimezone()
                        resource_available_time.last_edit_by_id = 1
                        resource_available_time.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        resource_available_time.is_active = True
                        resource_available_time.is_template = False
                        resource_available_time.weekday = str(
                            horarios["dia"] - 1
                        )
                        resource_available_time.resource_id = resource.id
                        resource_available_time.entry_time = (
                            horarios["dataInicioManha"]
                        )
                        resource_available_time.exit_time = (
                            horarios["dataFimManha"]
                        )
                        resource_available_time.closed = False
                        resource_available_time.save()

                        if resource_available_time_id is None:
                            criaTraducaoId(
                                "equipamento_horario_periodo",
                                horarios["id"],
                                "resource_available_time",
                                resource_available_time.id,
                            )
                        else:
                            atualizaTraducaoId(
                                "equipamento_horario_periodo",
                                horarios["id"],
                                "resource_available_time",
                                resource_available_time.id,
                            )
