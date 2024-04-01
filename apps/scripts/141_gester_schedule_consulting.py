import json
import os
import sys
from datetime import datetime, timedelta

import pytz
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
    CorporateGroupUnity, Partner, AccessUser,
    Sku,
    Schedule, ScheduleStatus, ScheduleSku, ScheduleSkuResource, ScheduleStatusDetail, Resource,
)


def verifica_horario_verao(data_agenda):
    data_format = datetime.strptime(data_agenda, '%d/%m/%Y')
    tz = pytz.timezone("Europe/Lisbon")
    horario_verao = tz.localize(data_format).dst() != timedelta(0)
    return horario_verao


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

# ACESSANDO A API #
headers = {
    "authorization": "Bearer " + access_token,
    "Content-Type": "application/json",
}
data = {"dataDe": "01/01/2000", "dataAte": "01/12/2030", "statusAgendamento": ["1", "2", "3", "4", "5", "6"],
        "servicoId": "1"}
url = 'http://onoderapt.swerp.com.br/api/agendamentos/lista'

response = requests.post(url=url, data=json.dumps(data), headers=headers)
agendamentos_list_json = response.json()

quant_total = len(agendamentos_list_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for agendamento_list_json in agendamentos_list_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    # ACESSANDO A API POR AGENDAMENTO #
    url_get = 'http://onoderapt.swerp.com.br/api/agendamentos/?id=' + str(agendamento_list_json["id"])

    response_get = requests.get(url=url_get, headers=headers)

    # PERCORRENDO TODOS OS CADASTROS DA LISTA #
    with transaction.atomic(using="gester"):
        if response_get.status_code == 200:
            response_agendamento_json = response_get.json()

            created_on = datetime.strptime(response_agendamento_json["dataCriacao"], "%d/%m/%Y às %H:%M")
            created_on_format = created_on.strftime("%Y-%m-%d %H:%M")

            if response_agendamento_json["dataAlteracao"] is not None and response_agendamento_json["dataAlteracao"] != "":
                last_edit_on = datetime.strptime(response_agendamento_json["dataAlteracao"], "%d/%m/%Y às %H:%M")
                last_edit_on_format = created_on.strftime("%Y-%m-%d %H:%M")
            else:
                last_edit_on_format = None

            if response_agendamento_json["colunaId"] is not None and response_agendamento_json["tratamentoId"] == "1":
                ### ATRIBUI OS VALORES PARA 'Schedule' ###
                schedule_id = leTraducaoId(
                    "appointments", response_agendamento_json["agendamentoId"], "schedule"
                )
                schedule = Schedule.objects.filter(id=schedule_id).first()

                if not schedule:
                    acao = colored("criado", "green")
                else:
                    acao = "atualizado"

                if not schedule or parametros.update_if_exists:
                    if not schedule:
                        schedule = Schedule()
                    schedule.created_on = created_on_format
                    schedule.last_edit_on = last_edit_on_format
                    schedule.is_active = True
                    schedule.is_template = False
                    schedule.comments = response_agendamento_json["observacoes"]
                    schedule.corporate_group_id = parametros.corporate_group_id
                    schedule.corporate_group_unity_id = corporate_group_unity.id
                    schedule.attendance_custumer_mood = "neutral"
                    schedule.attendance_custumer_comments = ""
                    schedule.session_number = 0
                    schedule.type = "consulting"
                    ### BUSCA ID DO CLIENTE ###
                    partner_customer = Partner.objects.filter(
                        id=leTraducaoId("pessoa", response_agendamento_json["pessoaId"], "partner")
                    ).first()
                    if partner_customer is not None:
                        schedule.partner_customer_id = partner_customer.id
                    else:
                        print(
                            colored(
                                f"Agendamento {response_agendamento_json['agendamentoId']}: "
                                f"cliente legado id {response_agendamento_json['pessoaId']} não importado",
                                "white",
                                "on_red",
                            )
                        )

                    ### BUSCA ID DO USUÁRIO ###
                    partner_user = Partner.objects.filter(
                        id=leTraducaoId("funcionario", response_agendamento_json["idUsuario"], "partner")
                    ).first()
                    access_user = AccessUser.objects.filter(
                        partner_id=partner_user.id if partner_user else 1
                    ).first()
                    if partner_user:
                        schedule.partner_user_id = partner_user.id
                        schedule.created_by_id = access_user.id if access_user else 1

                    data = datetime.strptime(response_agendamento_json["data"], "%d/%m/%Y")
                    hora = datetime.strptime(response_agendamento_json["hora"], "%H:%M")
                    data_hora = datetime(year=data.year, month=data.month, day=data.day,
                                         hour=hora.hour, minute=hora.minute, second=0)
                    schedule.begin_time = (
                                data_hora - timedelta(hours=4)
                                if verifica_horario_verao(response_agendamento_json["data"])
                                else data_hora - timedelta(hours=3)
                            )

                    schedule.attendance_time = 0
                    ### BUSCA A DURAÇÃO DO SERVIÇO ###
                    sku_servico = Sku.objects.filter(
                        id=leTraducaoId("servico", response_agendamento_json["tratamentoId"], "sku")
                    ).first()

                    if sku_servico is not None:
                        schedule.duration = sku_servico.default_working_time

                        ### FORMATA A DATA FINAL ###
                        duracao_servico = str(sku_servico.default_working_time)
                        horas, minutos, segundos = map(int, duracao_servico.split(":"))
                        duracao = timedelta(hours=horas, minutes=minutos, seconds=segundos)

                        inicio_agend = str(schedule.begin_time.time())
                        try:
                            h, m, s = map(int, inicio_agend.split(":"))
                            hora_agend = timedelta(hours=h, minutes=m, seconds=s)

                            final = hora_agend + duracao
                            final_str = (
                                    str(schedule.begin_time.date()) + " " + str(final) + " -0300"
                            )
                        except:
                            final_str = str(schedule.begin_time.date())

                        try:
                            schedule.end_time = datetime.strptime(
                                final_str, "%Y-%m-%d %H:%M:%S %z"
                            )
                        except:
                            schedule.end_time = schedule.begin_time
                    else:
                        print(f"Servico nao encontrado, ID: {response_agendamento_json['tratamntoId']}")
                        continue

                    # ATRIBUI O STATUS DO AGENDAMENTO #
                    status_name = ""

                    if response_agendamento_json["idStatus"] == '4':  # Executado
                        status_name = "finished"
                    elif response_agendamento_json["idStatus"] == '7':  # Excluido
                        status_name = "canceled"
                    elif response_agendamento_json["idStatus"] == '5':  # Faltou
                        status_name = "missed"
                    elif response_agendamento_json["idStatus"] == '2':  # Confirmado
                        status_name = "confirmed"
                    elif response_agendamento_json["idStatus"] == '1':  # Agendado
                        status_name = "scheduled"
                    elif response_agendamento_json["idStatus"] == '3':  # Presente
                        status_name = "confirmed"
                    else:
                        status_name = "paused"

                    if status_name == "finished":
                        schedule.attendance_start_time = schedule.begin_time
                        schedule.attendance_end_time = schedule.end_time

                    if status_name == "canceled":
                        schedule.is_active = False

                    schedule_status = ScheduleStatus.objects.get(
                        status=status_name, corporate_group_id=parametros.corporate_group_id
                    )

                    schedule.save()

                    if schedule_id is None:
                        criaTraducaoId(
                            "appointments",
                            response_agendamento_json["agendamentoId"],
                            "schedule",
                            schedule.id,
                        )
                    else:
                        atualizaTraducaoId(
                            "appointments",
                            response_agendamento_json["agendamentoId"],
                            "schedule",
                            schedule.id,
                        )

                    # CRIA REGISTRO schedule_sku - SERVIÇO DO AGENDAMENTO #
                    schedule_sku_id = leTraducaoId(
                        "appointments", response_agendamento_json["agendamentoId"], "schedule_sku"
                    )
                    schedule_sku = ScheduleSku.objects.filter(id=schedule_sku_id).first()

                    if not schedule_sku:
                        acao = colored("criado", "green")
                    else:
                        acao = "atualizado"

                    if not schedule_sku or parametros.update_if_exists:
                        if not schedule_sku:
                            schedule_sku = ScheduleSku()

                        schedule_sku.created_on = schedule.created_on
                        schedule_sku.created_by_id = schedule.created_by_id
                        schedule_sku.last_edit_on = schedule.last_edit_on
                        schedule_sku.last_edit_by_id = schedule.last_edit_by_id
                        schedule_sku.is_active = schedule.is_active
                        schedule_sku.is_template = False
                        schedule_sku.estimated_time = sku_servico.default_working_time
                        schedule_sku.corporate_group_id = parametros.corporate_group_id
                        schedule_sku.schedule_id = schedule.id
                        schedule_sku.sku_id = sku_servico.id
                        schedule_sku.save()

                        if schedule_sku_id is None:
                            criaTraducaoId(
                                "appointments",
                                response_agendamento_json["agendamentoId"],
                                "schedule_sku",
                                schedule_sku.id,
                            )
                        elif schedule_sku_id != schedule_sku.id:
                            atualizaTraducaoId(
                                "appointments",
                                response_agendamento_json["agendamentoId"],
                                "schedule_sku",
                                schedule_sku.id,
                            )

                    schedule_status_detail = ScheduleStatusDetail.objects.filter(
                        schedule_id=schedule.id
                    ).first()

                    if not schedule_status_detail:
                        schedule_status_detail = ScheduleStatusDetail()
                        schedule_status_detail.schedule_id = schedule.id
                        acao = colored("criado", "green")
                    else:
                        acao = "atualizado"

                    schedule_status_detail.schedule_status_id = schedule_status.id
                    schedule_status_detail.created_on = schedule.created_on
                    schedule_status_detail.created_by_id = schedule.created_by_id
                    schedule_status_detail.is_active = schedule.is_active
                    schedule_status_detail.is_template = False
                    schedule_status_detail.corporate_group_id = (
                        parametros.corporate_group_id
                    )
                    schedule_status_detail.save()

                    # Limpa recursos do agendamento, se já existir
                    acao = colored("criado", "green")
                    schedule_sku_resources = ScheduleSkuResource.objects.filter(
                        schedule_id=schedule.id
                    )
                    schedule_sku_resource: ScheduleSkuResource
                    for schedule_sku_resource in schedule_sku_resources:
                        schedule_sku_resource.delete()
                        acao = "atualizado"

                    ### CADASTRA O REGISTRO EM 'ScheduleSkuResource' ###
                    recurso_profissional = Resource.objects.filter(
                        id=leTraducaoId(
                            "consultor",
                            response_agendamento_json["colunaId"],
                            "resource",
                            corporate_group_unity.id,
                        )
                    ).first()
                    if not recurso_profissional:
                        print(
                            colored(
                                f"Agendamento {response_agendamento_json['agendamentoId']} consultor {response_agendamento_json['colunaId']} não encontrado",
                                "white",
                                "on_red",
                            )
                        )
                    else:
                        schedule_sku_professional = ScheduleSkuResource()
                        schedule_sku_professional.schedule_id = schedule.id
                        schedule_sku_professional.created_on = created_on_format
                        schedule_sku_professional.last_edit_on = last_edit_on_format
                        schedule_sku_professional.is_active = True
                        schedule_sku_professional.is_template = False
                        schedule_sku_professional.resource_id = (
                            recurso_profissional.id
                        )
                        schedule_sku_professional.schedule_id = schedule.id
                        schedule_sku_professional.sku_id = sku_servico.id
                        schedule_sku_professional.created_by_id = (
                            schedule.created_by_id
                        )
                        schedule_sku_professional.last_edit_by_id = (
                            schedule.last_edit_by_id
                        )
                        schedule_sku_professional.begin_time = (
                            schedule.begin_time
                        )
                        schedule_sku_professional.end_time = (
                            schedule.end_time
                        )
                        schedule_sku_professional.duration = (
                            schedule.duration
                        )
                        schedule_sku_professional.save()



