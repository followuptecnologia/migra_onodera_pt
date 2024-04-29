import json
import os
import sys

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

from apps.functions import leTraducaoId, traducaoUsuario

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, SalesOrder, AccessUser, Partner
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
data = {"dataDe": "01/01/2000", "dataAte": "31/12/2030", "pesquisaPor": ["1", "3", "2", "4"],
        "status": ["1", "3", "4", "5", "6", "7", "9", "12"]}
url = 'http://onoderapt.swerp.com.br/api/vendas/lista'

response = requests.post(url=url, data=json.dumps(data), headers=headers)
vendas_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(vendas_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for venda_json in vendas_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/vendas/" + str(venda_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_venda_json = response.json()

            sales_order_id = leTraducaoId("pedido", response_venda_json["id"], "sales_order")
            sales_order = SalesOrder.objects.filter(id=sales_order_id).first()

            access_user_id = traducaoUsuario(response_venda_json["vendedorId"])
            access_user = AccessUser.objects.filter(id=access_user_id).first()

            if sales_order:
                sales_order.partner_user_id = (
                    access_user.partner_id if access_user else None
                )
                sales_order.created_by_id = traducaoUsuario(response_venda_json["vendedorId"])
                sales_order.last_edit_by_id = traducaoUsuario(response_venda_json["vendedorId"])

                usuarioindicacao = AccessUser.objects.filter(
                    id=traducaoUsuario(response_venda_json["indicadoPorId"])
                ).first()
                if usuarioindicacao and Partner.objects.filter(id=usuarioindicacao.partner_id).exists():
                    sales_order.indicator_partner_id = (
                        usuarioindicacao.partner_id
                        if usuarioindicacao
                        else None
                    )

                sales_order.save()
