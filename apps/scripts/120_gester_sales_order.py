import json
import os
import sys
from datetime import datetime
from decimal import Decimal
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

from apps.functions import leTraducaoId, criaTraducaoId, atualizaTraducaoId, traducaoUsuario, ifNone

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, FinancePaymentOption, Partner, SalesOrder, AccessUser, CrmMedia, SalesOrderSku,
    FinanceTransactions, CashRegister, PartnerCustomerDocumentSale, Sku,
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

            ### ATRIBUI OS VALORES PARA 'SalesOrder' ###
            partner_id = leTraducaoId("pessoa", response_venda_json["pessoaId"], "partner")
            partner = Partner.objects.filter(id=partner_id).first()

            sales_order_id = leTraducaoId("pedido", response_venda_json["id"], "sales_order")
            sales_order = SalesOrder.objects.filter(id=sales_order_id).first()

            access_user_id = traducaoUsuario(response_venda_json["vendedorId"])
            access_user = AccessUser.objects.filter(id=access_user_id).first()

            if access_user is None:
                access_user = AccessUser.objects.get(id=1)

            if sales_order is None:
                acao = colored("criado", "green")
            else:
                acao = "atualizado"

            if sales_order is None or parametros.update_if_exists:
                if not sales_order:
                    sales_order = SalesOrder()

                crm_media_id = leTraducaoId(
                    "origem_media",
                    response_venda_json["origemMediaId"],
                    "crm_media",
                    corporate_group_unity.id,
                )
                crm_media = CrmMedia.objects.filter(id=crm_media_id).first()

                if partner:
                    partner.customer_type = Partner.CONVERTED_CUSTOMER

                sales_order.created_on = ifNone(
                    datetime.strptime(response_venda_json["data"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    datetime.now().astimezone()
                )
                sales_order.last_edit_on = ifNone(
                    datetime.strptime(response_venda_json["data"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    datetime.now().astimezone()
                )
                sales_order.created_by_id = traducaoUsuario(response_venda_json["vendedorId"])
                sales_order.last_edit_by_id = traducaoUsuario(response_venda_json["vendedorId"])
                sales_order.is_active = True
                sales_order.is_template = False
                sales_order.customer_name = (
                    ifNone(partner.name, f"Cliente {response_venda_json['pessoaId']}")
                    if partner
                    else f"Cliente {response_venda_json['pessoaId']}"
                )
                sales_order.total_list_price = 0
                sales_order.total_net_price = 0
                sales_order.total_effective_price = 0
                sales_order.comment = ifNone(response_venda_json["observacao"], "")
                sales_order.corporate_group_id = parametros.corporate_group_id
                sales_order.sale_date = datetime.strptime(response_venda_json["data"], "%d/%m/%Y").strftime(
                    "%Y-%m-%d")
                sales_order.total_price = ifNone(response_venda_json["total"], 0)
                sales_order.total_discount_price = ifNone(response_venda_json["desconto"], 0)
                sales_order.cancel_value = 0
                sales_order.exempt_fine = False
                sales_order.fine_value = 0
                sales_order.total_value_returned = 0
                sales_order.total_value_used = 0
                sales_order.corporate_group_unity_id = corporate_group_unity.id
                sales_order.order_status_service = ""
                sales_order.customer_partner_id = partner_id
                sales_order.partner_user_id = (
                    access_user.partner_id if access_user else None
                )
                sales_order.customer_phone = (
                    ifNone(partner.mobile, ifNone(partner.phone, "")) if partner else ""
                )
                sales_order.sales_media_id = crm_media.id if crm_media else None
                sales_order.sales_media_type_id = (
                    crm_media.media_group_id if crm_media else None
                )
                sales_order.credit_used = 0
                sales_order.has_courtesy = False
                sales_order.finished = False

                ## ATRIBUI O STATUS DA VENDA ##
                if response_venda_json["statusId"] == 7:  # "CANCELADO":
                    sales_order.order_status = "canceledSale"
                elif response_venda_json["statusId"] == 9:  # "VENDA RECEBIDA":
                    sales_order.order_status = "saleCompleted"
                elif response_venda_json["statusId"] == 3:  # "VENDA PENDENTE - PARCIAL":
                    sales_order.order_status = "partialSale"
                elif response_venda_json["statusId"] == 4:  # "VENDA PENDENTE - TOTAL":
                    sales_order.order_status = "totalPendingValue"
                elif response_venda_json["statusId"] == 1:  # "EM PROCESSAMENTO":
                    sales_order.order_status = "budget"
                elif response_venda_json["statusId"] == 5:  # "ORÇAMENTO PENDENTE":
                    sales_order.order_status = "budget"
                elif response_venda_json["statusId"] == 6:  # "ORÇAMENTO VENCIDO":
                    sales_order.order_status = "budget"
                else:
                    sales_order.order_status = "canceledSale"

                ## ATRIBUI SE A VENDA É SERVIÇO OU PRODUTO##
                sales_order.has_package = False
                sales_order.has_product = False
                sales_order.has_service = False
                for item_pedido in response_venda_json["itens"]:
                    if item_pedido["tipoItem"] == "Programa":
                        sales_order.has_package = True

                    if item_pedido["tipoItem"] == "Produto":
                        sales_order.has_product = True

                    if item_pedido["tipoItem"] == "Serviço":
                        sales_order.has_service = True

                ## USUÁRIO INDICADOR ##
                usuarioindicacao = AccessUser.objects.filter(
                    id=traducaoUsuario(response_venda_json["indicadoPorId"])
                ).first()
                if usuarioindicacao and Partner.objects.filter(id=usuarioindicacao.partner_id).exists():
                    sales_order.indicator_partner_id = (
                        usuarioindicacao.partner_id
                        if usuarioindicacao
                        else None
                    )

                ## CLIENTE INDICADOR ##
                clienteindicacao = Partner.objects.filter(
                    id=leTraducaoId("pessoa", response_venda_json["clienteIndicacaoId"], "partner")
                ).first()
                sales_order.indicator_customer_id = (
                    clienteindicacao.id
                    if clienteindicacao
                    else sales_order.indicator_customer_id
                )

                sales_order.save()

                sales_order.voucher_number = sales_order.id
                sales_order.save()

                if sales_order_id is None:
                    criaTraducaoId(
                        "pedido", response_venda_json["id"], "sales_order", sales_order.id
                    )
                else:
                    atualizaTraducaoId(
                        "pedido", response_venda_json["id"], "sales_order", sales_order.id
                    )

                if partner and crm_media and partner.media_id != crm_media.id:
                    partner.media_id = crm_media.id
                    partner.media_source_id = crm_media.media_group_id
                    partner.save()

            ## ATRIBUI OS VALORES PARA 'sales_order_sku ##
            for item in response_venda_json["itens"]:
                codigo_sku = item["itemId"]
                sales_order_sku_id = leTraducaoId(
                    f"pedido_item_{item['vendaId']}_{codigo_sku}",
                    item["id"],
                    "sales_order_sku",
                )
                sales_order_sku = SalesOrderSku.objects.filter(
                    id=sales_order_sku_id
                ).first()

                if sales_order_sku is None:
                    acao = colored("criado", "green")
                else:
                    acao = "atualizada"

                data_str = response_venda_json["data"]
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                sale_expiration_date = data_obj + relativedelta(
                    months=response_venda_json["validade"])

                if sales_order_sku is None or parametros.update_if_exists:
                    if not sales_order_sku:
                        sales_order_sku = SalesOrderSku()
                    sales_order_sku.created_on = sales_order.created_on
                    sales_order_sku.last_edit_on = sales_order.last_edit_on
                    sales_order_sku.created_by_id = sales_order.created_by_id
                    sales_order_sku.last_edit_by_id = sales_order.last_edit_by_id
                    sales_order_sku.is_active = True
                    sales_order_sku.is_template = False
                    sales_order_sku.quantity_sold = ifNone(item["quantidade"], 0)
                    sales_order_sku.quantity_used = 0
                    sales_order_sku.quantity_exchanged_for_credit = 0
                    sales_order_sku.quantity_scheduled = 0
                    sales_order_sku.quantity_available = ifNone(item["quantidade"], 0)
                    sales_order_sku.quantity_cancelled = 0
                    sales_order_sku.finished = False
                    sales_order_sku.price = ifNone(item["preco"], 0)
                    sales_order_sku.unit_list_price = ifNone(item["preco"], 0)
                    sales_order_sku.total_list_price = ifNone(
                        item["preco"], 0
                    ) * ifNone(item["quantidade"], 0)
                    sales_order_sku.discount_percent = 0
                    sales_order_sku.discount_percent = ifNone(
                        item["percentualDesconto"], 0
                    )
                    sales_order_sku.discount_value = ifNone(item["desconto"], 0)
                    sales_order_sku.total_net_price = 0
                    sales_order_sku.total_effective_price = 0
                    sales_order_sku.expiration_date = sale_expiration_date
                    sales_order_sku.can_add_discount = True
                    sales_order_sku.corporate_group_id = parametros.corporate_group_id
                    sales_order_sku.sales_order_id = sales_order.id
                    sales_order_sku.quantity_exchanged_for_credit = 0

                    if item["tipoItem"] == 'Serviço':
                        sales_order_sku.sku_id = leTraducaoId(
                            "servico", item["itemId"], "sku"
                        )
                    else:
                        sales_order_sku.sku_id = leTraducaoId(
                            "produto", item["itemId"], "sku"
                        )

                    sales_order_sku.updates_count = 0
                    sales_order_sku.is_courtesy = False
                    sales_order_sku.quantity_desconted = 0
                    sales_order_sku.has_cancelled = False
                    sales_order_sku.quantity_canceled_other_systems = 0
                    sales_order_sku.quantity_scheduled_exceeded = 0
                    sales_order_sku.save()

                    if sales_order_sku_id is None:
                        criaTraducaoId(
                            f"pedido_item_{item['vendaId']}_{codigo_sku}",
                            item["id"],
                            "sales_order_sku",
                            sales_order_sku.id,
                        )
                    elif sales_order_sku_id != sales_order_sku.id:
                        atualizaTraducaoId(
                            f"pedido_item_{item['vendaId']}_{codigo_sku}",
                            item["id"],
                            "sales_order_sku",
                            sales_order_sku.id,
                        )

            ## ATRIBUI OS VALORES PARA 'finance_transactions ##
            credit_used = 0
            total_parcelas = 0
            for pagamento in response_venda_json["pagamentos"]:
                ## VERIFICA SE FORMA DE PAGAMENTO É CRÉDITO DE CLIENTE ##
                if pagamento["formaPagamentoId"] == 7:
                    credit_used += pagamento["valor"]

                else:
                    finance_transactions_id = leTraducaoId(
                        "pedido_pagamento", pagamento["id"], "finance_transactions"
                    )
                    finance_transactions = FinanceTransactions.objects.filter(
                        id=finance_transactions_id
                    ).first()

                    if finance_transactions is None:
                        acao_finance = colored("criado", "green")
                    else:
                        acao_finance = "atualizado"

                    if pagamento["data"] is None:
                        if finance_transactions is not None:
                            finance_transactions.delete()
                        continue

                    if finance_transactions is None or parametros.update_if_exists:
                        total_parcelas += pagamento["valor"]
                        if finance_transactions is None:
                            finance_transactions = FinanceTransactions()
                        finance_transactions.created_on = sales_order.created_on
                        finance_transactions.last_edit_on = sales_order.last_edit_on
                        finance_transactions.created_by_id = sales_order.created_by_id
                        finance_transactions.last_edit_by_id = sales_order.last_edit_by_id
                        finance_transactions.is_active = True
                        finance_transactions.is_template = False
                        finance_transactions.is_paid = pagamento["recebido"]
                        finance_transactions.expiration_date = datetime.fromisoformat(
                            pagamento["dataLiquidacao"]).date()
                        finance_transactions.payment_date = datetime.fromisoformat(
                            pagamento["dataRecebimento"]).date()
                        finance_transactions.transaction_type = "income"
                        finance_transactions.payment_amount = pagamento["valor"]
                        finance_transactions.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        finance_transactions.corporate_group_unity_id = corporate_group_unity.id
                        finance_transactions.sales_order_id = sales_order.id
                        finance_transactions.finance_account_id = None
                        finance_transactions.finance_payment_option_id = (
                            leTraducaoId(
                                "forma_pagamento",
                                pagamento["formaPagamentoId"],
                                "finance_payment_option",
                                corporate_group_unity.id,
                            )
                            if leTraducaoId(
                                "forma_pagamento",
                                pagamento["formaPagamentoId"],
                                "finance_payment_option",
                                corporate_group_unity.id,
                            )
                               is not None
                            else 4
                        )
                        finance_transactions.customer_id = partner_id

                        ### CRIA 'cash_register' ###
                        cash_register = CashRegister.objects.filter(
                            opened_at=datetime.strptime(response_venda_json["data"], "%d/%m/%Y"),
                            corporate_group_unity_id=corporate_group_unity.id,
                        ).first()

                        if cash_register is None or parametros.update_if_exists:
                            if not cash_register:
                                acao = colored("criado", "green")
                                cash_register = CashRegister()
                                cash_register.created_on = sales_order.created_on
                                cash_register.last_edit_on = sales_order.last_edit_on
                                cash_register.created_by_id = 1
                                cash_register.last_edit_by_id = 1
                                cash_register.operator_id = 1
                                cash_register.is_active = False
                                cash_register.is_template = False
                                cash_register.status = "closed"
                                cash_register.opened_at = datetime.strptime(response_venda_json["data"], "%d/%m/%Y")
                                cash_register.initial_balance = 0
                                cash_register.balance = 0
                                cash_register.corporate_group_id = (
                                    parametros.corporate_group_id
                                )
                                cash_register.corporate_group_unity_id = (
                                    corporate_group_unity.id
                                )
                                cash_register.save()
                            else:
                                acao = "atualizado"
                            finance_transactions.cash_register_id = cash_register.id

                        finance_transactions.save()

                        if finance_transactions_id is None:
                            criaTraducaoId(
                                "pedido_pagamento",
                                pagamento["id"],
                                "finance_transactions",
                                finance_transactions.id,
                            )
                        elif finance_transactions.id != finance_transactions_id:
                            atualizaTraducaoId(
                                "pedido_pagamento",
                                pagamento["id"],
                                "finance_transactions",
                                finance_transactions.id,
                            )

            if credit_used > 0:
                sales_order.credit_used = credit_used
                sales_order.total_price = sales_order.total_price - credit_used
                sales_order.save()

            is_sale = ["saleCompleted", "totalPendingValue", "partialSale"]
            if (
                    total_parcelas < sales_order.total_price
                    and sales_order.order_status in is_sale
            ):
                sales_order.order_status = (
                    "partialSale" if total_parcelas > 0 else "totalPendingValue"
                )
                sales_order.save()
                pending_value = Decimal(sales_order.total_price) - Decimal(total_parcelas)
                if pending_value > 0:
                    option_pending_value = FinancePaymentOption.objects.filter(
                        type="pending_value",
                        corporate_group_unity_id=corporate_group_unity.id,
                    ).first()
                    if option_pending_value:
                        FinanceTransactions.objects.filter(
                            sales_order_id=sales_order.id,
                            finance_payment_option__type="pending_value",
                        ).delete()

                        finance_transactions = FinanceTransactions()
                        finance_transactions.created_on = sales_order.created_on
                        finance_transactions.last_edit_on = sales_order.last_edit_on
                        finance_transactions.created_by_id = sales_order.created_by_id
                        finance_transactions.last_edit_by_id = sales_order.last_edit_by_id
                        finance_transactions.is_active = True
                        finance_transactions.is_template = False
                        finance_transactions.is_paid = False
                        finance_transactions.expiration_date = sales_order.created_on
                        finance_transactions.payment_date = None
                        finance_transactions.transaction_type = "income"
                        finance_transactions.payment_amount = pending_value
                        finance_transactions.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        finance_transactions.corporate_group_unity_id = (
                            corporate_group_unity.id
                        )
                        finance_transactions.sales_order_id = sales_order.id
                        finance_transactions.finance_account_id = None
                        finance_transactions.finance_payment_option_id = (
                            option_pending_value.id
                        )
                        finance_transactions.customer_id = partner_id
                        finance_transactions.save()

            if (
                    total_parcelas == sales_order.total_price
                    and sales_order.order_status in is_sale
            ):
                sales_order.order_status = "saleCompleted"
                sales_order.save()

            if sales_order.order_status in ["saleCompleted", "partialSale"]:
                if not PartnerCustomerDocumentSale.objects.filter(
                        sales_order_id=sales_order.id, document_type__in=["contract", "receipt"]
                ).exists():
                    is_contract = False
                    for sale_sku in SalesOrderSku.objects.filter(
                            sales_order_id=sales_order.id
                    ):
                        sku = Sku.objects.filter(id=sale_sku.sku_id).first()
                        if sku and sale_sku.quantity_sold >= sku.quantity_generate_contract > 0:
                            is_contract = True

                    partner_customer_document_sale = PartnerCustomerDocumentSale()
                    partner_customer_document_sale.created_on = sales_order.created_on
                    partner_customer_document_sale.last_edit_on = sales_order.last_edit_on
                    partner_customer_document_sale.created_by_id = sales_order.created_by_id
                    partner_customer_document_sale.last_edit_by_id = (
                        sales_order.last_edit_by_id
                    )
                    partner_customer_document_sale.is_active = True
                    partner_customer_document_sale.is_template = False
                    partner_customer_document_sale.document_type = (
                        "contract" if is_contract else "receipt"
                    )
                    partner_customer_document_sale.document = None
                    partner_customer_document_sale.document_version = None
                    partner_customer_document_sale.sales_order_id = sales_order.id
                    partner_customer_document_sale.customer = None
                    partner_customer_document_sale.corporate_group_id = parametros.corporate_group_id
                    partner_customer_document_sale.save()
