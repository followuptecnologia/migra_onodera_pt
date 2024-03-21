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
    atualizaTraducaoId, ifNone,
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    SkuGroup, Sku, SkuServiceType, SkuSalesChannel, SkuCorporateGroupUnity, SkuEquipmentType, Resource,
    SkuServiceEquipment,
)


def convert_time(minutos):
    hour, min = divmod(minutos, 60)
    return "%d:%02d" % (hour, min)


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
data = {"nome": "", "tipo": ""}
url = 'http://onoderapt.swerp.com.br/api/servico/lista/?j={%22nome%22:%22%22,%22tipo%22:%22%22}'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
servicos_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(servicos_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for servico_json in servicos_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/servico/?id=" + str(servico_json["codigoServico"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_servico_json = response.json()

            sku_id = leTraducaoId("servico", response_servico_json["codigoServico"], "sku")
            sku = Sku.objects.filter(id=sku_id).first()
            if sku is None:
                sku = Sku.objects.filter(name=response_servico_json["descricaoServico"]).first()

            sku_service_type_id = leTraducaoId(
                "tipo_servico", response_servico_json["codigoTipoServico"], "sku_service_type"
            )
            sku_service_type = SkuServiceType.objects.filter(id=sku_service_type_id).first()

            sku_group_id = leTraducaoId(
                "tipo_agenda", response_servico_json["tipoAgendaId"], "sku_group"
            )
            sku_group = SkuGroup.objects.filter(id=sku_group_id).first()

            if not sku:
                acao = "criado"
            else:
                acao = "atualizado"

            # CRIA UM SKU PARA O SERVIÇO
            if sku is None or parametros.update_if_exists:
                if sku is None:
                    sku = Sku()
                    sku.created_on = datetime.now().astimezone()
                    sku.last_edit_on = datetime.now().astimezone()
                    sku.created_by_id = 1
                    sku.last_edit_by_id = 1
                    sku.is_active = response_servico_json["ativo"]
                    sku.is_template = False
                    sku.is_equipment = False
                    sku.is_product = False
                    sku.requires_prior_sale = response_servico_json["avulso"]
                    sku.requires_assessment_single_sale = response_servico_json["avulso"]
                    sku.requires_assessment_pre_sale = False
                    sku.requires_assessment_package_sale = False
                    sku.name = response_servico_json["descricaoServico"][:70]
                    sku.corporate_group_id = parametros.corporate_group_id
                    sku.description = response_servico_json["descricaoServico"]
                    sku.sales_price = 0
                    sku.default_working_time = ifNone(convert_time(response_servico_json["tempoTotal"]), 0)
                    sku.sku_number = response_servico_json["abreviacaoServico"]
                    sku.product_type = "sales_item"
                    sku.minimum_stock = 0
                    sku.assessment_service = (
                        True if response_servico_json["descricaoServico"].upper() == "AVALIAÇÃO" else False
                    )
                    sku.allow_single_sale = response_servico_json["avulso"]
                    sku.allow_package_sale = True

                    sku.demo_period_allowed = ifNone(convert_time(response_servico_json["tempoAtivdade"]), 0)
                    sku.allow_schedule_in_call_center = False
                    sku.allow_sale = True
                    sku.allow_courtesy = response_servico_json["cortesia"]
                    sku.allow_demonstration = response_servico_json["demostracao"]
                    sku.quantity_generate_contract = 0
                    sku.quantity_courtesy_per_year = 0
                    sku.allow_replacement = False
                    sku.need_sign = False
                    sku.sku_group_id = sku_group_id
                    sku.sku_service_type_id = sku_service_type_id
                    sku.save()

                    if sku_id is None:
                        criaTraducaoId("servico", response_servico_json["codigoServico"], "sku", sku.id)
                    elif sku_id != sku.id:
                        atualizaTraducaoId("servico", response_servico_json["codigoServico"], "sku", sku.id)

                    print(f"Sku (service) {sku.name} {acao}")

                if sku_id is None:
                    # ASSOCIA SKU AO CANAL DE VENDA PADRÃO
                    SkuSalesChannel.objects.using("gester").create(
                        created_on=datetime.now().astimezone(),
                        last_edit_on=datetime.now().astimezone(),
                        is_active=True,
                        is_template=False,
                        created_by_id=1,
                        last_edit_by_id=1,
                        sales_channel_id=parametros.default_sales_channel_id,  # A própria unidade
                        sku_id=sku.id,
                        corporate_group_id=parametros.corporate_group_id,
                    )

                sku_corporate_group_unity = SkuCorporateGroupUnity.objects.filter(
                    sku_id=sku.id,
                    corporate_group_unity_id=corporate_group_unity.id,
                ).first()

                if not sku_corporate_group_unity:
                    acao = "criado"
                else:
                    acao = "atualizado"

                # CRIA UM SKU PARA O SERVIÇO
                if sku_corporate_group_unity is None or parametros.update_if_exists:
                    if sku_corporate_group_unity is None:
                        sku_corporate_group_unity = SkuCorporateGroupUnity()
                        sku_corporate_group_unity.created_on = datetime.now().astimezone()
                        sku_corporate_group_unity.last_edit_on = datetime.now().astimezone()
                        sku_corporate_group_unity.created_by_id = 1
                        sku_corporate_group_unity.last_edit_by_id = 1
                        sku_corporate_group_unity.is_active = ifNone(response_servico_json["ativo"], False)
                        sku_corporate_group_unity.is_template = False
                        sku_corporate_group_unity.sku_id = sku.id
                        sku_corporate_group_unity.corporate_group_unity_id = corporate_group_unity.id
                        sku_corporate_group_unity.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        sku_corporate_group_unity.save()

                # RELACIONA O SKU (SERVIÇO) AOS EQUIPAMENTOS UTILIZADOS
                for maquina in response_servico_json["maquinas"]:
                    try:
                        sku_equipment_type = SkuEquipmentType.objects.filter(
                            id=leTraducaoId(
                                "maquina",
                                maquina["maquinaId"],
                                "sku_equipment_type",
                            )
                        ).first()

                        sku_equipment = Sku.objects.filter(
                            id=leTraducaoId(
                                "maquina_filial",
                                maquina["maquinaId"],
                                "sku_equipment_type",
                            )
                        ).first()

                        resource = (
                            Resource.objects.using("gester")
                            .filter(equipment=sku_equipment.id)
                            .first()
                        )

                        if not SkuServiceEquipment.objects.filter(
                                sku_equipment_type_id=sku_equipment_type.id,
                                sku_id=sku.id,
                        ).exists():
                            SkuServiceEquipment.objects.using("gester").create(
                                index=maquina["ordem"],
                                time=maquina["duracao"],
                                sku_equipment_type_id=sku_equipment_type.id,
                                sku_id=sku.id,
                            )

                    except:
                        pass

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
