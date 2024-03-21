import os, sys
import django
from termcolor import colored

PROJECT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.append(PROJECT_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings"

django.setup()

from apps.migrate.onodera.save.models import (
    SalesOrder, CorporateGroupUnity,
)
from apps.functions import *

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


def insert_balance(
    reason_type,
    movement_type,
    sales_order_sku_id,
    quantity,
    reason,
    description,
    schedule_id=None,
):
    SalesOrderSkuBalance.objects.create(
        is_active=True,
        is_template=False,
        created_on=datetime.now(),
        created_by_id=1,
        reason_type=reason_type,
        movement_type=movement_type,
        sales_order_sku_id=sales_order_sku_id,
        quantity=quantity,
        reason=reason,
        description=description,
        schedule_id=schedule_id,
        migration=True,
        corporate_group_id=parametros.corporate_group_id,
    )


sales_order = SalesOrder.objects.filter(
    corporate_group_unity_id=corporate_group_unity.id,
    order_status__in=[
        "saleCompleted",
        "partialSale",
        "demonstration",
        "replacement",
        "totalPendingValue",
        "canceledSale",
    ],
).order_by("-sale_date")

total = sales_order.count()
percent_ant = None
quant_lida = 0
print("TOTAL: ", total)

for sales in sales_order:
    quant_lida += 1
    percent = round((quant_lida / total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == total:
            print("")

    for sales_sku in SalesOrderSku.objects.filter(
        sales_order=sales, sku__is_product=False
    ):
        SalesOrderSkuBalance.objects.filter(sales_order_sku=sales_sku).exclude(
            reason__in=[
                "Troca de contrato por crédito",
                "Saldo Cancelado",
                "Transferência de contrato para outra unidade",
            ]
        ).delete()

        reason_status = (
            "Aquisição de novo contrato"
            if sales.order_status
            in ["saleCompleted", "partialSale", "totalPendingValue"]
            else "Demonstração adquirida"
            if sales.order_status == "demonstration"
            else "Reposição adquirida"
        )
        insert_balance(
            "entry", "entry", sales_sku.id, sales_sku.quantity_sold, reason_status, ""
        )

        schedule_sku_resource = ScheduleSkuResource.objects.filter(
            sales_order_sku=sales_sku
        ).values_list("schedule_id", flat=True)

        ## AGENDAMENTOS ##
        for schedule in set(schedule_sku_resource):
            schedule = Schedule.objects.get(id=schedule)

            schedule_status = list(
                schedule.status.all().values_list("status", flat=True)
            )

            ## AGENDADO ##
            if any(
                status in schedule_status
                for status in [
                    ScheduleStatus.SCHEDULED,
                    ScheduleStatus.CONFIRMED,
                    ScheduleStatus.PRESENT,
                    ScheduleStatus.PROGRESS,
                    ScheduleStatus.PAUSED,
                ]
            ):
                insert_balance(
                    "scheduling",
                    "exit",
                    sales_sku.id,
                    1,
                    "Serviço agendado",
                    "",
                    schedule.id,
                )
                sales_sku.quantity_scheduled += 1
                sales_sku.save()

            ## FALTOU. FALTOU CONFIRMADO e CANCELADO ##
            elif any(
                status in schedule_status
                for status in [
                    ScheduleStatus.MISSED,
                    ScheduleStatus.MISSED_CONFIRMED,
                    ScheduleStatus.CANCELED,
                ]
            ):
                reason_status = (
                    "Agendamento cancelado"
                    if "canceled" in schedule_status
                    else "Status alterado para Faltou"
                    if "missed" in schedule_status
                    else "Status alterado para Faltou Confirmado"
                )
                insert_balance(
                    "scheduling",
                    "exit",
                    sales_sku.id,
                    1,
                    "Serviço agendado",
                    "",
                    schedule.id,
                )
                insert_balance(
                    "scheduling_cancelled",
                    "entry",
                    sales_sku.id,
                    1,
                    reason_status,
                    "",
                    schedule.id,
                )

            ## FINALIZADO ##
            elif any(status in schedule_status for status in [ScheduleStatus.FINISHED]):
                insert_balance(
                    "scheduling",
                    "exit",
                    sales_sku.id,
                    1,
                    "Serviço agendado",
                    "",
                    schedule.id,
                )
                insert_balance(
                    "execution",
                    "exit",
                    sales_sku.id,
                    1,
                    "Agendamento executado (finalizado)",
                    "",
                    schedule.id,
                )
                sales_sku.quantity_used += 1
                sales_sku.save()

        ## TRANSFERENCIA DE CONTRATO ##
        if sales_sku.quantity_cancelled > 0:
            insert_balance(
                "discount",
                "exit",
                sales_sku.id,
                sales_sku.quantity_cancelled,
                "Saldo Cancelado",
                "",
            )
            sales_sku.quantity_desconted += sales_sku.quantity_cancelled
            sales_sku.save()

        quantity = (
            sales_sku.quantity_sold
            - sales_sku.quantity_desconted
            - sales_sku.quantity_used
            - sales_sku.quantity_scheduled
        )

        ## VENDA CANCELADA ##
        if sales.order_status == "saleCanceled" and quantity > 0:
            insert_balance(
                "discount", "exit", sales_sku.id, quantity, "Venda cancelada", ""
            )
            sales_sku.quantity_desconted += quantity
            sales_sku.save()

        ## SESSÃO UTILIZADA NO SISTEMA ANTERIOR ##
        if sales_sku.quantity_used_other_systems > 0:
            insert_balance(
                "scheduling",
                "exit",
                sales_sku.id,
                sales_sku.quantity_used_other_systems,
                "Serviço agendado",
                "Agendamento realizado no sistema anterior",
            )
            insert_balance(
                "execution",
                "exit",
                sales_sku.id,
                sales_sku.quantity_used_other_systems,
                "Agendamento executado (finalizado)",
                "Agendamento finalizado no sistema anterior",
            )
            sales_sku.quantity_used += sales_sku.quantity_used_other_systems
            sales_sku.quantity_used_other_systems = 0
            sales_sku.save()

        ## ATUALIZA QUANTIDADE DE EXECUÇÃO ##
        sales_sku.quantity_script_execution += 1
        sales_sku.quantity_cancelled = 0
        sales_sku.quantity_exchanged_for_credit = 0
        sales_sku.save()
