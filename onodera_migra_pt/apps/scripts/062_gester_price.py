import json
import os
import sys
from datetime import datetime
from decimal import Decimal

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
    PriceList, PriceListUnity, PriceListSku
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
    "username": f"1|master",
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
data = {"descricaoTabela": ""}
url = 'http://onoderapt.swerp.com.br/api/listapreco/tabelas'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
price_lists_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(price_lists_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for price_list_json in price_lists_json:
    url = "http://onoderapt.swerp.com.br/api/listapreco/tabela/" + str(price_list_json["codigoTabela"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_price_list_json = response.json()

            for unidade in response_price_list_json["unidades"]:
                if int(unidade["unidadeId"]) == parametros.codigofilial_sw and unidade["ativo"] is True:
                    price_list_current = response_price_list_json["id"]
                    break
                else:
                    price_list_current = None

            if price_list_current is None:
                continue

            price_list_id = leTraducaoId(
                "tabela_preco", response_price_list_json["id"], "price_list"
            )
            price_list = PriceList.objects.filter(id=price_list_id).first()

            if price_list_id is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if price_list is None or parametros.update_if_exists:
                ### ATRIBUI OS VALORES PARA 'PriceList' ###
                if price_list is None:
                    price_list = PriceList()
                    price_list.created_on = datetime.now().astimezone()
                    price_list.created_by_id = 1
                    price_list.last_edit_on = datetime.now().astimezone()
                    price_list.last_edit_by_id = 1
                    price_list.is_active = response_price_list_json["ativo"]
                    price_list.is_template = False
                    price_list.name = response_price_list_json["descricaoTabela"]
                    price_list.description = response_price_list_json["descricaoTabela"]
                    price_list.corporate_group_id = parametros.corporate_group_id
                    price_list.start_date = ifNone(
                        response_price_list_json["dataInicioVigencia"], "1901-01-01"
                    )
                    price_list.end_date = ifNone(response_price_list_json["dataFimVigencia"], "9999-12-31")
                    price_list.current = True
                    price_list.send_franchisor = True
                    price_list.send_franchisee = True
                    price_list.save()

                    if not price_list_id:
                        criaTraducaoId(
                            "tabela_preco",
                            response_price_list_json["id"],
                            "price_list",
                            price_list.id,
                        )
                    elif price_list_id != price_list.id:
                        atualizaTraducaoId(
                            "tabela_preco",
                            response_price_list_json["id"],
                            "price_list",
                            price_list.id,
                        )

            price_list_unity_id = leTraducaoId(
                "tabela_preco",
                response_price_list_json["id"],
                "price_list_unity",
                corporate_group_unity.id,
            )
            price_list_unity = PriceListUnity.objects.filter(id=price_list_unity_id).first()

            if price_list_unity_id is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if price_list_unity is None or parametros.update_if_exists:
                ### ATRIBUI OS VALORES PARA 'PriceList' ###
                if price_list_unity is None:
                    price_list_unity = PriceListUnity()
                    price_list_unity.created_on = datetime.now().astimezone()
                    price_list_unity.created_by_id = 1
                    price_list_unity.last_edit_on = datetime.now().astimezone()
                    price_list_unity.last_edit_by_id = 1
                    price_list_unity.is_active = True
                    price_list_unity.is_template = False
                    price_list_unity.price_list_id = price_list.id
                    price_list_unity.corporate_group_id = parametros.corporate_group_id
                    price_list_unity.corporate_group_unity_id = corporate_group_unity.id
                    price_list_unity.current = True
                    price_list_unity.save()

                    if not price_list_unity_id:
                        criaTraducaoId(
                            "tabela_preco",
                            response_price_list_json["id"],
                            "price_list_unity",
                            price_list_unity.id,
                            corporate_group_unity.id,
                        )
                    elif price_list_unity_id != price_list_unity.id:
                        atualizaTraducaoId(
                            "tabela_preco",
                            response_price_list_json["id"],
                            "price_list_unity",
                            price_list_unity.id,
                            corporate_group_unity.id,
                        )

            # PREÇOS DA TABELA
            for preco_item in response_price_list_json["itens"]:
                if preco_item["tipoItem"] == "P":
                    sku_id = leTraducaoId(
                        "produto", preco_item["itemId"], "sku"
                    )
                elif preco_item["tipoItem"] == "S":
                    sku_id = leTraducaoId(
                        "servico", preco_item["itemId"], "sku"
                    )
                else:
                    continue

                price_list_sku = PriceListSku.objects.filter(
                    price_list_id=price_list.id, sku_id=sku_id
                ).first()
                discount = preco_item["desconto"] * 100
                if not price_list_sku or parametros.update_if_exists:
                    if not price_list_sku and sku_id:
                        price_list_sku = PriceListSku()
                        price_list_sku.created_on = datetime.now().astimezone()
                        price_list_sku.created_by_id = 1
                        price_list_sku.last_edit_on = datetime.now().astimezone()
                        price_list_sku.last_edit_by_id = 1
                        price_list_sku.is_active = True
                        price_list_sku.corporate_group_id = parametros.corporate_group_id
                        price_list_sku.is_template = False
                        price_list_sku.price = preco_item["preco"]
                        price_list_sku.sku_id = sku_id
                        price_list_sku.price_list_id = price_list.id
                        price_list_sku.maximum_discount = preco_item["desconto"] * 100
                        price_list_sku.discount_price = (
                            Decimal(discount / 100)
                        ) * Decimal(preco_item["preco"])
                        price_list_sku.save()

                        print(f"PriceListSku {price_list_sku.id} {acao}")

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
