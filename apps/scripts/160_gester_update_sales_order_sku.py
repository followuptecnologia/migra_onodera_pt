import os
import sys
import django
from termcolor import colored

PROJECT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.append(PROJECT_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings"

django.setup()

from apps.functions import balance_sku

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity, SalesOrderSku,
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

sales_order_sku = SalesOrderSku.objects.filter(
    sales_order__corporate_group_unity_id=corporate_group_unity.id
)

total = sales_order_sku.count()
percent_ant = None
quant_lida = 0
print("TOTAL: ", total)

for sales in sales_order_sku:
    quant_lida += 1
    percent = round((quant_lida / total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == total:
            print("")

    try:
        quantities = balance_sku(sales.id)
    except:  # noqa
        quantities = None
    sales.quantity_used = (
        quantities["quantity_used"] if quantities else sales.quantity_used
    )
    sales.quantity_scheduled = (
        quantities["quantity_scheduled"] if quantities else sales.quantity_scheduled
    )
    sales.quantity_desconted = (
        quantities["quantity_desconted"] if quantities else sales.quantity_desconted
    )
    sales.save()

unity = CorporateGroupUnity.objects.get(id=corporate_group_unity.id)
unity.is_template = False
unity.save()
