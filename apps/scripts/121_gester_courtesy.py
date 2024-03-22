import json
import os
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

from apps.functions import leTraducaoId, criaTraducaoId, atualizaTraducaoId, ifNone

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, Partner, SalesOrder, AccessUser, SalesOrderSku,
    Sku, PartnerUnityCustomer, SalesDiscountSku,
    LegacyTranslateId, PriceListUnity, PriceListSku,
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

# PERCORRE OS CLIENTES PARA LISTAR AS CORTESIAS POR CLIENTE #
customers = PartnerUnityCustomer.objects.filter(corporate_group_unity_id=corporate_group_unity.id)
quant_total = customers.count()
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for customer in customers:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    partner = Partner.objects.filter(id=customer.partner_id).first()

    pessoa_legacy = LegacyTranslateId.objects.filter(
        legacy_table="pessoa",
        gester_table="partner",
        gester_id=partner.id
    ).first()
    if not pessoa_legacy:
        continue

    # ACESSANDO A API #
    headers = {
        "authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }
    data = {"id": pessoa_legacy.legacy_id, "nomePessoa": partner.name}
    url = 'http://onoderapt.swerp.com.br/api/clientes/cortesias'

    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    cortesias_json = response.json()

    # PERCORRENDO TODOS OS CADASTROS DA LISTA #
    for cortesia_json in cortesias_json["cortesias"]:
        with transaction.atomic(using="gester"):
            ### ATRIBUI OS VALORES PARA 'SalesOrder' ###
            sales_order_id = leTraducaoId(
                "pessoa_cortesia", cortesia_json["id"], "sales_order"
            )
            sales_order = SalesOrder.objects.filter(id=sales_order_id).first()
            access_user = AccessUser.objects.filter(id=1).first()

            if sales_order is None:
                acao = colored("criado", "green")
            else:
                acao = "atualizado"

            if sales_order is None or parametros.update_if_exists:
                if not sales_order:
                    sales_order = SalesOrder()
                sales_order.created_on = cortesia_json["data"]
                sales_order.last_edit_on = cortesia_json["data"]
                sales_order.created_by_id = 1
                sales_order.last_edit_by_id = 1
                sales_order.is_active = True
                sales_order.is_template = False
                sales_order.customer_name = partner.name
                sales_order.total_list_price = 0
                sales_order.total_net_price = 0
                sales_order.total_effective_price = 0
                sales_order.corporate_group_id = parametros.corporate_group_id
                sales_order.sale_date = cortesia_json["data"]
                sales_order.total_price = 0
                sales_order.total_discount_price = 100
                sales_order.cancel_value = 0
                sales_order.exempt_fine = False
                sales_order.fine_value = 0
                sales_order.total_value_returned = 0
                sales_order.total_value_used = 0
                sales_order.corporate_group_unity_id = corporate_group_unity.id
                sales_order.order_status_service = ""
                sales_order.customer_partner_id = partner.id
                sales_order.partner_user_id = access_user.partner_id
                sales_order.customer_phone = (
                    ifNone(partner.mobile, ifNone(partner.phone, "")) if partner else ""
                )
                sales_order.sales_media_id = None
                sales_order.sales_media_type_id = None
                sales_order.finished = False
                sales_order.has_package = False
                sales_order.has_product = False
                sales_order.has_service = True
                sales_order.discount_reason = ifNone(cortesia_json["motivo"], "")
                sales_order.credit_used = 0
                sales_order.has_courtesy = True
                sales_order.comment = ifNone(cortesia_json["observacao"], "")
                sales_order.save()
                sales_order.voucher_number = sales_order.id

                ## CANCELADO ##
                if cortesia_json["status"] == "CANCELADO":
                    sales_order.order_status = "canceledSale"
                    sales_order.has_courtesy = True
                ## REPOSIÇÃO
                elif cortesia_json["motivoId"] in ('7', '8', '9'):
                    sales_order.order_status = "replacement"
                    sales_order.has_courtesy = False
                ## DEMONSTRAÇÃO
                elif cortesia_json["motivoId"] == '12':
                    sales_order.order_status = "demonstration"
                    sales_order.has_courtesy = False
                ## CORTESIA
                else:
                    sales_order.order_status = "saleCompleted"
                    sales_order.has_courtesy = True

                sales_order.save()

                if sales_order_id is None:
                    criaTraducaoId(
                        "pessoa_cortesia", cortesia_json["id"], "sales_order", sales_order.id
                    )
                else:
                    atualizaTraducaoId(
                        "pessoa_cortesia", cortesia_json["id"], "sales_order", sales_order.id
                    )

            ## ATRIBUI OS VALORES PARA 'sales_order_sku ##
            sales_order_sku_id = leTraducaoId(
                f"pessoa_cortesia", cortesia_json["id"], "sales_order_sku"
            )
            sales_order_sku = SalesOrderSku.objects.filter(id=sales_order_sku_id).first()

            data_obj = datetime.strptime(cortesia_json["data"], "%Y-%m-%dT%H:%M:%S")
            sale_expiration_date = data_obj + relativedelta(months=6)

            if sales_order_sku is None:
                acao = colored("criado", "green")
            else:
                acao = "atualizada"

            sku = Sku.objects.filter(name=cortesia_json["nomeServico"]).first()
            if not sku:
                print(
                    colored(
                        f"Serviço {cortesia_json['nomeServico']} não encontrado",
                        "red"
                    )
                )
                continue

            # BUSCA O VALOR DO SKU EM 'PriceListSku' NA TABELA CORRENTE DA UNIDADE #
            price_list_unity = PriceListUnity.objects.filter(
                corporate_group_unity_id=corporate_group_unity.id,
                current=True,
            ).first()

            price_list_sku = PriceListSku.objects.filter(
                sku_id=sku.id,
                price_list_id=price_list_unity.price_list_id,
            ).first()

            if sales_order_sku is None or parametros.update_if_exists:
                if not sales_order_sku:
                    sales_order_sku = SalesOrderSku()
                sales_order_sku.created_on = sales_order.created_on
                sales_order_sku.last_edit_on = sales_order.last_edit_on
                sales_order_sku.created_by_id = sales_order.created_by_id
                sales_order_sku.last_edit_by_id = sales_order.last_edit_by_id
                sales_order_sku.is_active = True
                sales_order_sku.is_template = False
                sales_order_sku.quantity_sold = cortesia_json["quantidade"]
                sales_order_sku.quantity_used = 0
                sales_order_sku.quantity_exchanged_for_credit = 0
                sales_order_sku.quantity_scheduled = 0
                sales_order_sku.quantity_available = cortesia_json["quantidade"]
                sales_order_sku.quantity_cancelled = 0
                sales_order_sku.quantity_desconted = 0
                sales_order_sku.finished = False
                sales_order_sku.price = price_list_sku.price if price_list_sku else 0
                sales_order_sku.unit_list_price = 0
                sales_order_sku.total_list_price = 0
                sales_order_sku.discount_percent = 100
                sales_order_sku.discount_value = (price_list_sku.price if price_list_sku else 0) * cortesia_json["quantidade"]
                sales_order_sku.total_net_price = 0
                sales_order_sku.total_effective_price = 0
                sales_order_sku.expiration_date = sale_expiration_date
                sales_order_sku.can_add_discount = True
                sales_order_sku.corporate_group_id = parametros.corporate_group_id
                sales_order_sku.sales_order_id = sales_order.id
                sales_order_sku.quantity_exchanged_for_credit = 0
                sales_order_sku.sku_id = sku.id
                sales_order_sku.updates_count = 0

                ## REPOSIÇÃO e DEMONSTRAÇÃO
                if cortesia_json["motivoId"] in ('7', '8', '9', '12'):
                    sales_order_sku.is_courtesy = False
                    sales_order_sku.courtesy_reason = ""
                ## CORTESIA
                else:
                    sales_order_sku.is_courtesy = True
                    sales_order_sku.courtesy_reason = ifNone(cortesia_json["motivo"], "")

                sales_order_sku.save()

                if sales_order_sku_id is None:
                    criaTraducaoId(
                        f"pessoa_cortesia",
                        cortesia_json["id"],
                        "sales_order_sku",
                        sales_order_sku.id,
                    )
                elif sales_order_sku_id != sales_order_sku.id:
                    atualizaTraducaoId(
                        f"pessoa_cortesia",
                        cortesia_json["id"],
                        "sales_order_sku",
                        sales_order_sku.id,
                    )

                if sales_order_sku.is_courtesy:
                    SalesDiscountSku.objects.filter(
                        sale_order_sku_id=sales_order_sku.id
                    ).delete()
                    SalesDiscountSku.objects.create(
                        created_on=sales_order_sku.created_on,
                        last_edit_on=sales_order_sku.last_edit_on,
                        is_active=True,
                        is_template=False,
                        quantity=0,
                        discount_percent=100,
                        discount_value=(price_list_sku.price if price_list_sku else 0) * cortesia_json["quantidade"],
                        editable=True,
                        removable=True,
                        corporate_group_id=parametros.corporate_group_id,
                        created_by_id=sales_order_sku.created_by_id,
                        last_edit_by_id=sales_order_sku.last_edit_by_id,
                        sales_discount_id=None,
                        sales_order_id=sales_order_sku.sales_order_id,
                        sale_order_sku_id=sales_order_sku.id,
                        sku_id=sales_order_sku.sku_id,
                    )
