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
    SkuGroup, Sku
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
url = 'http://onoderapt.swerp.com.br/api/lista/tipoproduto/'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
products_groups_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(products_groups_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

# CRIA GRUPOS DE PRODUTOS (SKU_GROUP)
for product_group_json in products_groups_json:
    # Transação atômica
    with transaction.atomic(using="gester"):
        sku_group_id = leTraducaoId("familia", product_group_json["id"], "sku_group")
        sku_group = SkuGroup.objects.filter(id=sku_group_id).first()

        if not sku_group or parametros.update_if_exists:
            if not sku_group:
                sku_group = SkuGroup()
                sku_group.created_on = datetime.now().astimezone()
                sku_group.created_by_id = 1
                sku_group.last_edit_on = datetime.now().astimezone()
                sku_group.last_edit_by_id = 1
                sku_group.is_template = False
                sku_group.is_active = True
                sku_group.type = "product"
                sku_group.name = ifNone(product_group_json["descricao"], "")
                sku_group.abbreviated_name = ""
                sku_group.corporate_group_id = parametros.corporate_group_id
                sku_group.form_after_service_id = None
                sku_group.form_before_service_id = None
                sku_group.save()

                if sku_group_id is None:
                    criaTraducaoId(
                        "familia", product_group_json["id"], "sku_group", sku_group.id
                    )
                elif sku_group_id != sku_group.id:
                    atualizaTraducaoId(
                        "familia", product_group_json["id"], "sku_group", sku_group.id
                    )

                print(f"SkuGroup {sku_group.name} - CRIADO")

## MIGRA OS PRODUTOS ##
headers = {
    "authorization": "Bearer " + access_token,
    "Content-Type": "application/json",
}
data = {"nome": ""}
url = 'http://onoderapt.swerp.com.br/api/produto/lista/?j={%22nome%22:%22%22}'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
products_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(products_json)
percent_ant = None
quant_lida = 0
print("TOTAL PRODUTOS: ", quant_total)

for product_json in products_json:
    url = "http://onoderapt.swerp.com.br/api/produto/?id=" + str(product_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_product_json = response.json()
            sku_group_id = leTraducaoId("familia", response_product_json["familia"], "sku_group")

            if sku_group_id:
                sku_id = leTraducaoId("produto", response_product_json["codigo"], "sku")
                sku = Sku.objects.filter(id=sku_id).first()

                if not sku:
                    sku = Sku.objects.filter(name=response_product_json["nome"]).first()

                if not sku or parametros.update_if_exists:
                    if not sku:
                        sku = Sku()
                        acao = "criado"

                        sku.created_on = datetime.now().astimezone()
                        sku.created_by_id = 1
                        sku.last_edit_on = datetime.now().astimezone()
                        sku.last_edit_by_id = 1
                        sku.is_template = False
                        sku.is_active = response_product_json["ativo"]
                        sku.name = ifNone(response_product_json["nome"], "")[:70]
                        sku.default_working_time = "00:00:00"
                        sku.sku_number = ""
                        sku.requires_prior_sale = False
                        sku.is_equipment = False
                        sku.is_product = True
                        sku.brand = ""
                        sku.product_type = "sales_item"
                        sku.description = ifNone(response_product_json["descricao"], "")
                        sku.bar_code = ""
                        sku.gtin_code = ""
                        sku.internal_code = ""
                        sku.ncm = ""
                        sku.minimum_stock = 0
                        sku.sales_price = 0
                        sku.corporate_group_id = parametros.corporate_group_id
                        sku.sku_group_id = sku_group_id
                        sku.sku_service_type_id = None
                        sku.ums_id = None
                        sku.sku_equipment_type_id = None
                        sku.consent_terms = ""
                        sku.assessment_service = False
                        sku.allow_single_sale = True
                        sku.allow_package_sale = True
                        sku.demo_period_allowed = "00:00:00"
                        sku.allow_schedule_in_call_center = False
                        sku.allow_sale = False
                        sku.allow_courtesy = False
                        sku.allow_demonstration = False
                        sku.quantity_generate_contract = 0
                        sku.quantity_courtesy_per_year = 0
                        sku.allow_replacement = False
                        sku.need_sign = False
                        sku.save()
                    else:
                        acao = "atualizado"

                    if sku_id is None:
                        criaTraducaoId("produto", response_product_json["codigo"], "sku", sku.id)
                    elif sku_id != sku.id:
                        atualizaTraducaoId("produto", response_product_json["codigo"], "sku", sku.id)

                    print(f"Sku (produto) {sku.description} {acao}")


print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
