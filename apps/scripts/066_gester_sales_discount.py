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
    atualizaTraducaoId, ifNone
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    SalesDiscount,
    SalesDiscountPackageSku, PriceListUnity, PriceListSku, SalesDiscountUnity, SalesDiscountCampaign,
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
data = {"nome": "", "tipo": ""}
url = 'http://onoderapt.swerp.com.br/api/programas/lista/?j={%22nome%22:%22%22,%22tipo%22:%22%22}'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
programas_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(programas_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for programa_json in programas_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/programas/?id=" + str(programa_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_programa_json = response.json()
            sales_discount_id = leTraducaoId("programa", response_programa_json["id"], "sales_discount")
            sales_discount = SalesDiscount.objects.filter(id=sales_discount_id).first()

            if sales_discount is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if sales_discount is None or parametros.update_if_exists:
                ### ATRIBUI OS VALORES PARA 'SalesDiscount' ###
                if not sales_discount:
                    sales_discount = SalesDiscount()
                    sales_discount.created_on = datetime.now().astimezone()
                    sales_discount.last_edit_on = datetime.now().astimezone()
                    sales_discount.is_active = response_programa_json["ativo"]
                    sales_discount.is_template = False
                    sales_discount.type = "package"
                    sales_discount.name = ifNone(response_programa_json["nomePrograma"], "")
                    sales_discount.description = ifNone(response_programa_json["nomePrograma"], "")
                    sales_discount.display_in_separate_services = False
                    sales_discount.maximum_discount_packages = 0
                    sales_discount.display_in_products = False
                    sales_discount.display_in_packages = False
                    sales_discount.maximum_discount_products = 0
                    sales_discount.unity_limit = False
                    sales_discount.document_number_limit = False
                    sales_discount.customer_limit = False
                    sales_discount.restrict_services = False
                    sales_discount.payment_forms_limit = False
                    sales_discount.allow_customer_without_ftn = True
                    sales_discount.allow_birthday_person = False
                    sales_discount.allow_another_discount_reason = False
                    sales_discount.affects_comission = False
                    sales_discount.display_discount_reason_on = "site"
                    sales_discount.campaign_linked = False
                    sales_discount.regulation = "."
                    sales_discount.send_franchisee = False
                    sales_discount.send_franchisor = False
                    sales_discount.initial_date = datetime.strptime(response_programa_json["validadeDe"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    sales_discount.final_date = datetime.strptime(response_programa_json["validadeAte"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    sales_discount.validity_days = 365
                    sales_discount.generate_cashback = False
                    sales_discount.enable_buy_and_win = False
                    sales_discount.corporate_group_id = parametros.corporate_group_id
                    sales_discount.maximum_discount_separate_services = 0
                    sales_discount.created_by_id = 1
                    sales_discount.last_edit_by_id = 1
                    sales_discount.generate_contract = False
                    sales_discount.total_value = 0
                    sales_discount.save()

                    if sales_discount_id is None:
                        criaTraducaoId(
                            "programa", response_programa_json["id"], "sales_discount", sales_discount.id
                        )
                    else:
                        atualizaTraducaoId(
                            "programa", response_programa_json["id"], "sales_discount", sales_discount.id
                        )

                    print(f"SalesDiscount {sales_discount.description} {acao}")

                    ### ATRIBUI OS VALORES PARA 'SalesDiscountPackageSku' ###
                    for item in response_programa_json["itens"]:
                        ### ATRIBUI O ID DO SKU ###
                        if item["produtoId"] is not None and item["produtoId"] != "":
                            sku_id = leTraducaoId(
                                "produto", item["produtoId"], "sku"
                            )
                        elif item["servicoId"] is not None and item["servicoId"] != "":
                            sku_id = leTraducaoId(
                                "servico", item["servicoId"], "sku"
                            )
                        else:
                            sku_id = None
                            print(f"SKU NÃO ENCONTRADO PARA O PACOTE: {response_programa_json['nomePrograma']}")
                            continue

                        sales_discount_package_sku_id = leTraducaoId(
                            f"programa_item_fixo_{item['programaId']}",
                            sku_id,
                            "sales_discount_package_sku",
                            corporate_group_unity.id,
                        )
                        sales_discount_package_sku = SalesDiscountPackageSku.objects.filter(
                            id=sales_discount_package_sku_id
                        ).first()

                        if sales_discount_package_sku is None:
                            acao = "criado"
                        else:
                            acao = "atualizado"

                        if (
                            sales_discount_package_sku is None
                            or parametros.update_if_exists
                        ):
                            if not sales_discount_package_sku:
                                sales_discount_package_sku = SalesDiscountPackageSku()
                                sales_discount_package_sku.created_on = (
                                    datetime.now().astimezone()
                                )
                                sales_discount_package_sku.last_edit_on = (
                                    datetime.now().astimezone()
                                )
                                sales_discount_package_sku.is_active = response_programa_json["ativo"]
                                sales_discount_package_sku.is_template = False
                                sales_discount_package_sku.quantity = item["quantidade"]
                                sales_discount_package_sku.corporate_group_id = (
                                    parametros.corporate_group_id
                                )
                                sales_discount_package_sku.sales_discount_id = (
                                    sales_discount.id
                                )
                                sales_discount_package_sku.created_by_id = 1
                                sales_discount_package_sku.last_edit_by_id = 1

                                sales_discount_package_sku.sku_id = sku_id

                                ### BUSCA O VALOR DO SKU EM 'PriceListSku' NA TABELA CORRENTE DA UNIDADE ###
                                price_list_unity = PriceListUnity.objects.filter(
                                    corporate_group_unity_id=corporate_group_unity.id,
                                    current=True,
                                ).first()

                                price_list_sku = PriceListSku.objects.filter(
                                    sku_id=sku_id,
                                    price_list_id=price_list_unity.price_list_id,
                                ).first()

                                ### IDENTIFICA SE O DESCONTO É % OU $ ###
                                if price_list_sku is None or price_list_sku.price == 0:
                                    sales_discount_package_sku.discount_value = 0
                                    sales_discount_package_sku.discount_percent = 0
                                else:
                                    sales_discount_package_sku.discount_percent = item["valor"]
                                    sales_discount_package_sku.discount_value = (
                                        (Decimal(item["valor"]) / 100)
                                        * price_list_sku.price
                                    ) * item["quantidade"]

                                sales_discount_package_sku.save()

                                if sales_discount_package_sku_id is None:
                                    criaTraducaoId(
                                        f"programa_item_fixo_{item['programaId']}",
                                        sku_id,
                                        f"sales_discount_package_sku",
                                        sales_discount_package_sku.id,
                                        corporate_group_unity.id,
                                    )
                                else:
                                    atualizaTraducaoId(
                                        f"programa_item_fixo_{item['programaId']}",
                                        sku_id,
                                        f"sales_discount_package_sku",
                                        sales_discount_package_sku.id,
                                        corporate_group_unity.id,
                                    )

                                print(
                                    f"SalesDiscountPackageSku {sales_discount_package_sku.id} {acao}"
                                )

            ### ATRIBUI OS VALORES PARA 'SalesDiscountUnity' ###
            sales_discount_unity_id = leTraducaoId(
                "programa_filial",
                response_programa_json["id"],
                "sales_discount_unit",
                corporate_group_unity.id,
            )
            sales_discount_unity = SalesDiscountUnity.objects.filter(
                id=sales_discount_unity_id
            ).first()

            if sales_discount_unity is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if sales_discount_unity is None or parametros.update_if_exists:
                if not sales_discount_unity:
                    sales_discount_unity = SalesDiscountUnity()
                    sales_discount_unity.created_on = datetime.now().astimezone()
                    sales_discount_unity.last_edit_on = datetime.now().astimezone()
                    sales_discount_unity.is_active = ifNone(response_programa_json["ativo"], False)
                    sales_discount_unity.is_template = False
                    sales_discount_unity.corporate_group_id = parametros.corporate_group_id
                    sales_discount_unity.corporate_group_unity_id = corporate_group_unity.id
                    sales_discount_unity.sales_discount_id = sales_discount.id
                    sales_discount_unity.created_by_id = 1
                    sales_discount_unity.last_edit_by_id = 1

                    sales_discount_unity.save()

                    if sales_discount_unity_id is None:
                        criaTraducaoId(
                            "programa_filial",
                            response_programa_json["id"],
                            "sales_discount_unit",
                            sales_discount_unity.id,
                            corporate_group_unity.id,
                        )
                    else:
                        atualizaTraducaoId(
                            "programa_filial",
                            response_programa_json["id"],
                            "sales_discount_unit",
                            sales_discount_unity.id,
                            corporate_group_unity.id,
                        )

            ### ATRIBUI OS VALORES PARA 'SalesDiscountCampaign' ###
            sales_discount_campaign_id = leTraducaoId(
                "programa", response_programa_json["id"], "sales_discount_campaign"
            )
            sales_discount_campaign = SalesDiscountCampaign.objects.filter(
                id=sales_discount_campaign_id
            ).first()

            if sales_discount_campaign is None:
                acao = "criado"
            else:
                acao = "atualizado"

            if sales_discount_campaign is None or parametros.update_if_exists:
                if not sales_discount_campaign:
                    sales_discount_campaign = SalesDiscountCampaign()
                    sales_discount_campaign.created_on = datetime.now().astimezone()
                    sales_discount_campaign.last_edit_on = datetime.now().astimezone()
                    sales_discount_campaign.is_active = response_programa_json["ativo"]
                    sales_discount_campaign.is_template = False
                    sales_discount_campaign.initial_date = datetime.strptime(response_programa_json["validadeDe"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    sales_discount_campaign.final_date = datetime.strptime(response_programa_json["validadeAte"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    sales_discount_campaign.regulation = "<p>---</p>"
                    sales_discount_campaign.send_franchisor = False
                    sales_discount_campaign.send_franchisee = False
                    sales_discount_campaign.corporate_group_id = 1
                    sales_discount_campaign.sales_discount_id = sales_discount.id
                    sales_discount_campaign.created_by_id = 1
                    sales_discount_campaign.last_edit_by_id = 1

                    sales_discount_campaign.save()

                if sales_discount_campaign_id is None:
                    criaTraducaoId(
                        "programa",
                        response_programa_json["id"],
                        "sales_discount_campaign",
                        sales_discount_campaign.id,
                    )
                else:
                    atualizaTraducaoId(
                        "programa",
                        response_programa_json["id"],
                        "sales_discount_campaign",
                        sales_discount_campaign.id,
                    )

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
