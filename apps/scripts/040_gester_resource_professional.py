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

from apps.functions import (
    leTraducaoId,
    criaTraducaoId,
    atualizaTraducaoId, ifNone
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    Resource,
    AccessUser, Partner, PartnerUnityUser, AccessProfile, ResourcePerformsSku,
    ResourceAvailableTime,
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
url = 'http://onoderapt.swerp.com.br/api/colunas'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
colunas_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(colunas_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)

for coluna_json in colunas_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    url = "http://onoderapt.swerp.com.br/api/colunas/" + str(coluna_json["id"])
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_coluna_json = response.json()

            access_user_id = leTraducaoId("funcionario", response_coluna_json["usuarioId"], "access_user")
            access_user = AccessUser.objects.filter(id=access_user_id).first()

            if response_coluna_json and response_coluna_json["usuarioId"] is None or access_user is None:
                access_user_id = leTraducaoId("consultor", response_coluna_json["id"], "access_user")
                access_user = AccessUser.objects.filter(id=access_user_id).first()

                url = "http://onoderapt.swerp.com.br/api/colaboradores/" + str(response_coluna_json["usuarioId"])
                response = requests.get(url=url, headers=headers)
                response_colaborador_json = response.json()

                try:
                    if response_colaborador_json["sexo"] == "MASCULINO":
                        sexo = "male"
                    elif response_colaborador_json["sexo"] == "FEMININO":
                        sexo = "female"
                    else:
                        sexo = "female"
                except:
                    sexo = "female"

                if not access_user:
                    access_user = AccessUser()
                    partner = Partner()
                    acao = "criado"

                    try:
                        if response_coluna_json["nome"] is not None:
                            pessoa_nomes = response_coluna_json["usuarioId"].split(" ", 1)
                        else:
                            pessoa_nomes = []
                    except:
                        pessoa_nomes = []

                    partner.created_on = datetime.now().astimezone()
                    partner.last_edit_on = datetime.now().astimezone()
                    partner.created_by_id = 1
                    partner.last_edit_by_id = 1
                    partner.is_active = ifNone(response_coluna_json["ativo"], True)
                    partner.is_template = False
                    partner.name = ifNone(response_coluna_json["nome"], "")
                    partner.first_name = pessoa_nomes[0] if len(pessoa_nomes) >= 1 else ""
                    partner.last_name = pessoa_nomes[1] if len(pessoa_nomes) >= 2 else ""
                    try:
                        partner.login_name = ifNone(response_colaborador_json["login"], f"login_{response_coluna_json['usuarioId']}")
                    except:
                        partner.login_name = f"login_{response_coluna_json['usuarioId']}"
                    partner.password = "SEM SENHA"
                    partner.person_type = "natural"
                    #   partner.federal_tax_number = ifNone(format_cpf(response_colaborador_json["cpf"]), "")
                    partner.state_tax_number = ""
                    partner.city_tax_number = ""
                    partner.federal_register_number = ""
                    partner.birth_date = None
                    partner.genre = sexo
                    partner.mobile = f"351{response_colaborador_json['celular']}"
                    partner.phone = f"351{response_colaborador_json['telefone']}"
                    partner.business_phone = ""
                    partner.whatsapp_number = ""
                    partner.trade_name = ""
                    partner.marital_status = ""
                    partner.email = ifNone(response_colaborador_json['email'], f"consultor_{response_coluna_json['id']}@onodera.com.br")
                    partner.schedule_notification_mail = False
                    partner.schedule_notification_whatsapp = False
                    partner.schedule_notification_sms = False
                    partner.media_source_id = None
                    partner.customer_responsible_name = ""
                    partner.customer_responsible_legal_id = None
                    partner.is_customer = False
                    partner.is_supplier = False
                    partner.is_employee = True
                    partner.is_user = True
                    partner.is_sales_representative = True
                    partner.is_corporate_unity = False
                    partner.is_unity_owner = False
                    partner.is_professional = True
                    partner.work_card = None
                    partner.serial_number = None
                    partner.pis = None
                    partner.transportation_voucher = ""
                    partner.meal_voucher = ""
                    partner.other_voucher = ""
                    partner.bank = ""
                    partner.agency = ""
                    partner.checking_account = ""
                    partner.foreign_tax_number = ifNone(response_colaborador_json["cpf"], "")
                    partner.identity_card_number = ""
                    partner.issuing_agency = ""
                    partner.receive_email = False
                    partner.receive_sms = False
                    partner.receive_whats = False
                    partner.classification = ""
                    partner.cell_phone_operator = ""
                    partner.point_registry = False
                    partner.corporate_group_id = parametros.corporate_group_id
                    partner.customer_corporate_unity_id = None
                    partner.customer_last_attendant_unity_id = None
                    partner.main_unit_id = None
                    partner.media_id = None
                    partner.referral_customer_id = None
                    partner.supplier_corporate_unity_id = None
                    partner.type_media_id = None
                    partner.federal_tax_document_type_id = None
                    partner.federal_register_document_type_id = None
                    partner.foreign_tax_document_type_id = None
                    partner.occupation = ""
                    partner.employee_salary = 0
                    partner.customer_id = 0
                    partner.classification = "new"
                    partner.have_federal_tax_number = True
                    partner.address = ""
                    partner.address_number = ""
                    partner.address_neighborhood = ""
                    partner.address_complement = ""
                    partner.zip_code = ""
                    partner.location_country_id = parametros.location_country_id
                    partner.investor_only = False
                    partner.description = "migração recurso sem usuário"
                    partner.whatsapp_integration_code = ""
                    partner.save()
                    criaTraducaoId("consultor", response_coluna_json["id"], "partner", partner.id)

                    user_name = response_coluna_json["nome"].split(" ", 1)
                    access_user.accepted_terms = False
                    access_user.corporate_group_id = parametros.corporate_group_id
                    access_user.current_unity_id = corporate_group_unity.id
                    access_user.date_joined = "1901-01-01 00:00"
                    access_user.email = f"consultor_{response_coluna_json['id']}@onodera.com.br"
                    access_user.first_name = user_name[0] if len(user_name) > 1 else ""
                    access_user.forgot_password_hash = None
                    access_user.forgot_password_expire = None
                    access_user.is_active = response_coluna_json["ativo"]
                    access_user.is_staff = True
                    access_user.is_superuser = False
                    access_user.last_login = None
                    access_user.last_name = user_name[1] if len(user_name) >= 2 else ""
                    access_user.partner_id = partner.id if partner else None
                    access_user.password = "SEM SENHA"
                    access_user.phone_number = ""
                    access_user.username = f"consultor_{response_coluna_json['id']}"
                    access_user.is_franchisor_user = False
                    access_user.save()
                if access_user_id is None:
                    criaTraducaoId("consultor", response_coluna_json["id"], "access_user", access_user.id)
                else:
                    atualizaTraducaoId(
                        "consultor", response_coluna_json["id"], "access_user", access_user.id
                    )

                partner = access_user.partner
                # RELACIONAMENTO ENTRE USUARIO E UNIDADE #
                partner_unity_user = PartnerUnityUser.objects.filter(
                    partner_id=partner.id,
                    corporate_group_unity_id=corporate_group_unity.id,
                ).first()

                if partner_unity_user is None:
                    acao = "criada"
                else:
                    acao = "atualizada"

                other_unity = PartnerUnityUser.objects.filter(
                    partner_id=partner.id
                ).exclude(corporate_group_unity_id=corporate_group_unity.id)
                if (not other_unity.exists() and response_coluna_json["usuarioId"] is False) or response_coluna_json["ativo"] is True:
                    if partner_unity_user is None or parametros.update_if_exists:
                        if not partner_unity_user:
                            partner_unity_user = PartnerUnityUser()
                            access_profile_id = leTraducaoId(
                                "funcao", response_colaborador_json['perfil'], "access_profile"
                            )
                            if not access_profile_id:
                                access_profile_id = (
                                    AccessProfile.objects.filter(
                                        name="OPERADOR",
                                        corporate_group_id=parametros.corporate_group_id,
                                    )
                                    .first()
                                    .id
                                )

                            partner_unity_user.created_by_id = 1
                            partner_unity_user.created_on = partner.created_on
                            partner_unity_user.last_update_by_id = 1
                            partner_unity_user.last_edit_on = partner.last_edit_on
                            partner_unity_user.is_active = partner.is_active
                            partner_unity_user.is_template = False
                            partner_unity_user.access_profile_id = access_profile_id
                            partner_unity_user.corporate_group_id = (
                                parametros.corporate_group_id
                            )
                            partner_unity_user.corporate_group_unity_id = corporate_group_unity.id
                            partner_unity_user.partner_id = partner.id

                            partner_unity_user.save()

            else:
                access_user_id = leTraducaoId(
                    "funcionario", response_coluna_json["usuarioId"], "access_user"
                )
                access_user = AccessUser.objects.filter(id=access_user_id).first()
                partner = Partner.objects.filter(id=access_user.partner_id).first()

            # CRIA RESOURCE, SE ELE AINDA NÃƒO EXISTE
            resource_id = leTraducaoId(
                "consultor", response_coluna_json["id"], "resource", corporate_group_unity.id
            )
            resource = Resource.objects.filter(id=resource_id).first()

            if resource is None or parametros.update_if_exists:
                if not resource:
                    resource = Resource()
                    resource.created_on = datetime.now().astimezone()
                    resource.created_by_id = 1
                    resource.is_active = ifNone(response_coluna_json["ativo"], False)
                    resource.is_template = False
                    resource.name = response_coluna_json["nome"]
                    resource.is_consultant = True
                    resource.type = "professional"
                    resource.serial_number = ""
                    resource.specific_control = ""
                    resource.has_schedule_control = True
                    resource.equipment_sku_id = None
                    resource.partner_id = partner.id if partner else None
                    resource.corporate_group_id = parametros.corporate_group_id
                    resource.corporate_group_unity_id = corporate_group_unity.id
                    resource.save()

                if resource_id is None:
                    criaTraducaoId(
                        "consultor",
                        response_coluna_json["id"],
                        "resource",
                        resource.id,
                        corporate_group_unity.id,
                    )
                elif resource_id != resource.id:
                    atualizaTraducaoId(
                        "consultor",
                        response_coluna_json["id"],
                        "resource",
                        resource.id,
                        corporate_group_unity.id,
                    )

                    print(f"Registro resource {resource.name} CRIADO")

                ### PERCORRE TODOS OS REGISTROS 'ServicoColuna' ###
                if response_coluna_json["servicos"]:
                    for servico in response_coluna_json["servicos"]:
                        # Verifica chave duplicada
                        resource_performs_sku = ResourcePerformsSku.objects.filter(
                            resource_id=resource.id,
                            sku_service_id=leTraducaoId(
                                "servico", servico["codigoServico"], "sku"
                            ),
                            corporate_group_unity_id=corporate_group_unity.id,
                        ).first()

                        if not resource_performs_sku:
                            resource_performs_sku_id = leTraducaoId(
                                "consultor_servico",
                                servico["id"],
                                "resource_performs_sku",
                                corporate_group_unity.id,
                            )
                            resource_performs_sku = ResourcePerformsSku.objects.filter(
                                id=resource_performs_sku_id
                            ).first()

                            sku_id = leTraducaoId(
                                        "servico", servico["codigoServico"], "sku"
                                    )
                            ### ATRIBUI OS VALORES PARA 'ResourcePerformsSku' ###
                            if not resource_performs_sku or parametros.update_if_exists:
                                if not resource_performs_sku and sku_id is not None:
                                    resource_performs_sku = ResourcePerformsSku()
                                    resource_performs_sku.created_on = (
                                        datetime.now().astimezone()
                                    )
                                    resource_performs_sku.last_edit_on = (
                                        datetime.now().astimezone()
                                    )
                                    resource_performs_sku.is_active = True
                                    resource_performs_sku.is_template = False
                                    resource_performs_sku.corporate_group_id = (
                                        parametros.corporate_group_id
                                    )
                                    resource_performs_sku.corporate_group_unity_id = corporate_group_unity.id
                                    resource_performs_sku.resource_id = resource.id
                                    resource_performs_sku.sku_service_id = leTraducaoId(
                                        "servico", servico["codigoServico"], "sku"
                                    )
                                    resource_performs_sku.created_by_id = 1
                                    resource_performs_sku.last_edit_by_id = 1
                                    resource_performs_sku.save()

                                    if not resource_performs_sku_id:
                                        criaTraducaoId(
                                            "consultor_servico",
                                            servico["id"],
                                            "resource_performs_sku",
                                            resource_performs_sku.id,
                                            corporate_group_unity.id,
                                        )
                                    else:
                                        atualizaTraducaoId(
                                            "consultor_servico",
                                            servico["codigoServico"],
                                            "resource_performs_sku",
                                            resource_performs_sku.id,
                                            corporate_group_unity.id,
                                        )

            # Horários (disponibilidade) do consultor
            for horario in response_coluna_json["horarios"]:

                if horario["isTrabalha"] is False:
                    continue

                resource_available_time_id = leTraducaoId(
                    "consultor_horario_periodo",
                    horario["id"],
                    "resource_available_time",
                )
                resource_available_time = ResourceAvailableTime.objects.filter(
                    id=resource_available_time_id
                ).first()

                if not resource_available_time:
                    acao = colored("criado", "green")
                else:
                    acao = "atualizado"

                if not resource_available_time or parametros.update_if_exists:
                    if not resource_available_time:
                        resource_available_time = ResourceAvailableTime()
                        resource_available_time.created_on = datetime.now().astimezone()
                        resource_available_time.created_by_id = 1
                        resource_available_time.last_edit_on = datetime.now().astimezone()
                        resource_available_time.last_edit_by_id = 1
                        resource_available_time.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        resource_available_time.is_active = True
                        resource_available_time.is_template = False
                        resource_available_time.weekday = str(
                           horario["dia"] - 1
                        )
                        resource_available_time.resource_id = resource.id
                        resource_available_time.entry_time = (
                            horario["dataInicioManha"]
                        )
                        resource_available_time.exit_time = (
                            horario["dataFimTarde"]
                        )
                        resource_available_time.break_entry_time = (
                           horario["dataFimManha"]
                        )
                        resource_available_time.break_time = (
                            horario["dataInicioTarde"]
                        )
                        resource_available_time.closed = False

                        resource_available_time.save()

                        if (
                            resource_available_time.break_time
                            == resource_available_time.break_entry_time
                        ):
                            ResourceAvailableTime.objects.filter(
                                id=resource_available_time.id
                            ).update(break_time=None, break_entry_time=None)

                        if resource_available_time_id is None:
                            criaTraducaoId(
                                "consultor_horario_periodo",
                                horario["id"],
                                "resource_available_time",
                                resource_available_time.id,
                            )
                        else:
                            atualizaTraducaoId(
                                "consultor_horario_periodo",
                                horario["id"],
                                "resource_available_time",
                                resource_available_time.id,
                            )

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
