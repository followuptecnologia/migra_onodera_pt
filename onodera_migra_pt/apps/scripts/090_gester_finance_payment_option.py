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

from apps.functions import leTraducaoId, criaTraducaoId, atualizaTraducaoId

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, FinancePaymentOption,
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
url = 'http://onoderapt.swerp.com.br/api/lista/formaspagamento'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
formas_pagamento_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(formas_pagamento_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for forma_pagamento_json in formas_pagamento_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    with transaction.atomic(using="gester"):
        finance_payment_option_id = leTraducaoId(
            "forma_pagamento",
            forma_pagamento_json["id"],
            "finance_payment_option",
            corporate_group_unity.id,
        )
        finance_payment_option = FinancePaymentOption.objects.filter(
            id=finance_payment_option_id
        ).first()

        if finance_payment_option is None:
            acao = "criada"
        else:
            acao = "atualizada"

        if finance_payment_option is None or parametros.update_if_exists:
            if not finance_payment_option:
                finance_payment_option = FinancePaymentOption()
                finance_payment_option.created_by_id = 1
                finance_payment_option.created_on = datetime.now().astimezone()
                finance_payment_option.last_edit_by_id = 1
                finance_payment_option.last_edit_on = datetime.now().astimezone()
                finance_payment_option.is_template = False
                finance_payment_option.is_active = True
                finance_payment_option.allowed_for_purchase = True
                finance_payment_option.allowed_for_sale = True
                finance_payment_option.corporate_group_id = (
                    parametros.corporate_group_id
                )
                finance_payment_option.corporate_group_unity_id = corporate_group_unity.id
                finance_payment_option.finance_account_id = None
                finance_payment_option.is_change_allowed = False
                finance_payment_option.is_recurrent = False
                finance_payment_option.max_number_of_installments = forma_pagamento_json["maximoParcela"]
                finance_payment_option.min_number_of_installments = 1
                finance_payment_option.name = forma_pagamento_json["nome"]
                finance_payment_option.auto_payable = False

                if forma_pagamento_json["nome"] == "Cartão de Crédito":
                    finance_payment_option.type = "credit_card"
                elif forma_pagamento_json["nome"] == "Cartão Débito":
                    finance_payment_option.type = "debit_card"
                elif forma_pagamento_json["nome"] == "Boleto":
                    finance_payment_option.type = "bank_slip"
                elif forma_pagamento_json["nome"] == "Cheque":
                    finance_payment_option.type = "check"
                elif forma_pagamento_json["nome"] == "Depósito":
                    finance_payment_option.type = "deposit"
                elif forma_pagamento_json["nome"] == "Transferência":
                    finance_payment_option.type = "bank_transfer"
                else:
                    finance_payment_option.type = "cash"

                finance_payment_option.save()

                if finance_payment_option_id is None:
                    criaTraducaoId(
                        "forma_pagamento",
                        forma_pagamento_json["id"],
                        "finance_payment_option",
                        finance_payment_option.id,
                        corporate_group_unity.id,
                    )
                else:
                    atualizaTraducaoId(
                        "forma_pagamento",
                        forma_pagamento_json["id"],
                        "finance_payment_option",
                        finance_payment_option.id,
                        corporate_group_unity.id,
                    )

                print(f"FinancePaymentOption {finance_payment_option.name} {acao}")

## CRIA FORMA DE PGTO 'VALOR PENDENTE' ##
option_pending_value = FinancePaymentOption.objects.filter(
    type="pending_value", corporate_group_unity_id=corporate_group_unity.id
)
if not option_pending_value:
    finance_payment_option = FinancePaymentOption()
    finance_payment_option.created_by_id = 1
    finance_payment_option.created_on = datetime.now().astimezone()
    finance_payment_option.last_edit_by_id = 1
    finance_payment_option.last_edit_on = datetime.now().astimezone()
    finance_payment_option.is_template = False
    finance_payment_option.is_active = True
    finance_payment_option.allowed_for_purchase = False
    finance_payment_option.allowed_for_sale = True
    finance_payment_option.corporate_group_id = parametros.corporate_group_id
    finance_payment_option.corporate_group_unity_id = corporate_group_unity.id
    finance_payment_option.finance_account_id = None
    finance_payment_option.is_change_allowed = False
    finance_payment_option.is_recurrent = False
    finance_payment_option.max_number_of_installments = 1
    finance_payment_option.min_number_of_installments = 1
    finance_payment_option.name = "Valor Pendente"
    finance_payment_option.auto_payable = False
    finance_payment_option.type = "pending_value"
    finance_payment_option.save()

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
