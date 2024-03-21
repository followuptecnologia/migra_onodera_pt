import os
import sys
from datetime import datetime

from django.db import transaction
from termcolor import colored
import django

PROJECT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.append(PROJECT_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "apps.settings"

django.setup()

from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    Partner, PartnerUnityUser,
    ResourceAvailableTime, HumanResourceWorkingHour,
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

partners_unity = PartnerUnityUser.objects.filter(
    corporate_group_unity_id=corporate_group_unity.id,
    partner__point_registry=False,
)

print(f"Total: {partners_unity.count()}")
quant_total = partners_unity.count()
percent_ant = None
quant_lida = 0

for partner in partners_unity:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    with transaction.atomic(using="gester"):
        resource_available_time = ResourceAvailableTime.objects.filter(
            resource__partner_id=partner.partner_id
        )

        if resource_available_time:
            Partner.objects.filter(id=partner.partner_id).update(point_registry=True)
            for time in resource_available_time:
                human_resource_working_hour = HumanResourceWorkingHour.objects.filter(
                    partner_id=partner.partner_id, weekday=time.weekday
                ).first()

                if not human_resource_working_hour:
                    human_resource_working_hour = HumanResourceWorkingHour()
                    human_resource_working_hour.created_on = datetime.now().astimezone()
                    human_resource_working_hour.created_by_id = 1
                    human_resource_working_hour.last_edit_on = (
                        datetime.now().astimezone()
                    )
                    human_resource_working_hour.last_edit_by_id = 1
                    human_resource_working_hour.corporate_group_id = (
                        parametros.corporate_group_id
                    )
                    human_resource_working_hour.is_active = True
                    human_resource_working_hour.is_template = False
                    human_resource_working_hour.weekday = time.weekday
                    human_resource_working_hour.partner_id = partner.partner_id
                    human_resource_working_hour.entry_time = time.entry_time
                    human_resource_working_hour.break_time = time.break_time
                    human_resource_working_hour.break_entry_time = time.break_entry_time
                    human_resource_working_hour.exit_time = time.exit_time
                    human_resource_working_hour.closed = False
                    human_resource_working_hour.save()


print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
