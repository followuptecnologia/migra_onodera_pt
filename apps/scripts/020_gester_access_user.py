import json
import os
import sys
from datetime import datetime

from django.db import transaction
from django.db.models import Q
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
    format_phone,
    criaTraducaoId,
    atualizaTraducaoId,
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    Partner,
    LocationCity,
    LocationState,
    LocationCountry,
    PartnerUnityUser,
    AccessProfile,
    AccessPermission,
    AccessProfilePermission,
    AccessUser,
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
data = {"nome": " "}
url = 'http://onoderapt.swerp.com.br/api/colaboradores/lista?j={"nome":"","perfilUsuario":[],"mostrarPor":["1","0"],"e":"Braga"}'

response = requests.get(url=url, data=json.dumps(data), headers=headers)
colaboradores_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(colaboradores_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for colaborador_json in colaboradores_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")
    url = "http://onoderapt.swerp.com.br/api/colaboradores/" + str(
        colaborador_json["id"]
    )
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        with transaction.atomic(using="gester"):
            response_colaborador_json = response.json()
            data_admissao = datetime.strptime(
                response_colaborador_json["dataAdmissao"], "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
            ## CRIA OS PERFIS ##
            access_profile = AccessProfile.objects.filter(
                name=response_colaborador_json["nomeGrupo"]
            ).first()
            if not access_profile:
                access_profile = AccessProfile()
                access_profile.created_on = datetime.now().astimezone()
                access_profile.created_by_id = 1
                access_profile.is_active = True
                access_profile.is_template = False
                access_profile.corporate_group_id = parametros.corporate_group_id
                access_profile.name = response_colaborador_json["nomeGrupo"]
                access_profile.is_base = True
                access_profile.save()

                permissoes = AccessPermission.objects.filter(
                    is_active=True, corporate_group_id=parametros.corporate_group_id
                )
                for permissao in permissoes:
                    profile_permission = AccessProfilePermission.objects.filter(
                        access_permission_id=permissao.id,
                        access_profile_id=access_profile.id,
                    ).first()
                    if not profile_permission:
                        profile_permission = AccessProfilePermission()
                        profile_permission.created_on = datetime.now().astimezone()
                        profile_permission.last_edit_on = datetime.now().astimezone()
                        profile_permission.created_by_id = 1
                        profile_permission.last_edit_by_id = 1
                        profile_permission.is_active = True
                        profile_permission.is_template = False
                        profile_permission.is_granted = True
                        profile_permission.can_grant = True
                        profile_permission.can_see = True
                        profile_permission.access_permission_id = permissao.id
                        profile_permission.access_profile_id = access_profile.id
                        profile_permission.corporate_group_id = (
                            parametros.corporate_group_id
                        )
                        profile_permission.save()

            partner_id = leTraducaoId(
                "funcionario", response_colaborador_json, "partner"
            )
            partner = Partner.objects.filter(id=partner_id).first()

            location_city = LocationCity.objects.filter(
                name=response_colaborador_json["municipio"]
            ).first()

            if location_city:
                location_state = LocationState.objects.filter(
                    id=location_city.location_state_id
                ).first()
            else:
                location_state = None

            if location_state:
                location_country = LocationCountry.objects.filter(
                    id=location_state.location_country_id
                ).first()
            else:
                location_country = LocationCountry.objects.filter(
                    id=parametros.location_country_id
                ).first()

            if location_country is None:
                location_country = LocationCountry.objects.filter(
                    id=parametros.location_country_id
                ).first()

            if not partner:
                acao = "criado"
            else:
                acao = "atualizado"

            if partner is None or parametros.update_if_exists:
                if partner is None:
                    partner = Partner()

                    if response_colaborador_json["sexo"] == "FEMININO":
                        genre = "female"
                    elif response_colaborador_json["sexo"] == "MASCULINO":
                        genre = "male"
                    else:
                        genre = "female"

                    # partner.is_active = ifNone(usuario.ativo, True)
                    partner.is_active = response_colaborador_json["ativo"]
                    partner.is_template = False
                    partner.name = response_colaborador_json["nome"].upper()
                    partner.login_name = response_colaborador_json["login"]
                    partner.federal_tax_number = ""
                    partner.foreign_tax_number = response_colaborador_json["cpf"]
                    partner.birth_date = (
                        datetime.strptime(
                            response_colaborador_json["dataNascimento"], "%d/%m/%Y"
                        ).strftime("%Y-%m-%d")
                        if response_colaborador_json["dataNascimento"] != ""
                        else None
                    )
                    partner.genre = genre
                    partner.mobile = str(location_country.idd_code) + format_phone(
                        response_colaborador_json["celular"]
                    )
                    partner.phone = str(location_country.idd_code) + format_phone(
                        response_colaborador_json["telefone"]
                    )
                    partner.whatsapp_number = str(
                        location_country.idd_code
                    ) + format_phone(response_colaborador_json["celular"])
                    partner.address = response_colaborador_json["endereco"]
                    partner.address_number = response_colaborador_json["numero"]
                    partner.address_neighborhood = response_colaborador_json["bairro"]
                    partner.address_complement = response_colaborador_json[
                        "complemento"
                    ]
                    partner.zip_code = response_colaborador_json["cep"]
                    partner.location_country_id = location_country.id
                    partner.location_city_id = (
                        location_city.id if location_city else None
                    )
                    partner.location_state_id = (
                        location_state.id if location_state else None
                    )
                    partner.email = response_colaborador_json["email"]
                    partner.is_customer = False
                    partner.is_supplier = False
                    partner.is_employee = True
                    partner.is_user = True
                    partner.is_corporate_unity = False
                    partner.is_unity_owner = False
                    partner.corporate_group_id = parametros.corporate_group_id
                    partner.is_professional = True
                    partner.description = response_colaborador_json["observacao"]
                    partner.receive_email = False
                    partner.receive_sms = False
                    partner.receive_whats = False
                    partner.main_unit_id = corporate_group_unity.id
                    partner.point_registry = False
                    partner.employee_salary = 0
                    partner.have_federal_tax_number = False
                    partner.created_on = data_admissao
                    partner.investor_only = False
                    partner.occupation = ""
                    partner.password = "SEM SENHA"
                    partner.person_type = "natural"
                    partner.whatsapp_integration_code = ""
                    partner.social_name = ""

                    if response_colaborador_json["tipoContrato"] == 1:
                        partner.type_contract = "autonomous"
                    elif response_colaborador_json["tipoContrato"] == 2:
                        partner.type_contract = "trainee"
                    elif response_colaborador_json["tipoContrato"] == 3:
                        partner.type_contract = "registered"
                    elif response_colaborador_json["tipoContrato"] == 4:
                        partner.type_contract = "temporary"
                    else:
                        partner.type_contract = ""

                    partner.save()

                else:
                    partner.is_employee = True
                    partner.person_type = "natural"
                    partner.save()

                if partner_id is None:
                    criaTraducaoId(
                        "funcionario",
                        response_colaborador_json["id"],
                        "partner",
                        partner.id,
                    )
                else:
                    atualizaTraducaoId(
                        "funcionario",
                        response_colaborador_json["id"],
                        "partner",
                        partner.id,
                    )

            # RELACIONAMENTO ENTRE USUARIO E UNIDADE #
            partner_unity_user = PartnerUnityUser.objects.filter(
                partner_id=partner.id,
                corporate_group_unity_id=corporate_group_unity.id,
            ).first()

            if partner_unity_user is None:
                acao = "criada"
            else:
                acao = "atualizada"

            if partner_unity_user is None:
                partner_unity_user = PartnerUnityUser()
                partner_unity_user.created_by_id = 1
                partner_unity_user.created_on = partner.created_on
                partner_unity_user.last_update_by_id = 1
                partner_unity_user.last_edit_on = partner.last_edit_on
                partner_unity_user.is_active = response_colaborador_json["ativo"]
                partner_unity_user.is_template = False
                partner_unity_user.access_profile_id = access_profile.id
                partner_unity_user.corporate_group_id = parametros.corporate_group_id
                partner_unity_user.corporate_group_unity_id = corporate_group_unity.id
                partner_unity_user.partner_id = partner.id
                partner_unity_user.save()

            #  Se existe usuário associado, cria também no gester
            if response_colaborador_json["login"] != "":
                access_user = AccessUser.objects.filter(partner_id=partner.id).first()
                if not access_user or parametros.update_if_exists:
                    user_name = response_colaborador_json["nome"].split(" ", 1)

                    partner.is_user = True
                    partner.save(force_update=True)

                    ### CADASTRA O COLABORADOR EM 'AccesUser' ###
                    ### ATRIBUI OS VALORES PARA 'AccesUser' ###
                    if not access_user:
                        access_user = AccessUser()
                        access_user.email = response_colaborador_json["email"]
                        access_user.accepted_terms = False
                        access_user.corporate_group_id = parametros.corporate_group_id
                        access_user.current_unity_id = corporate_group_unity.id
                        access_user.date_joined = data_admissao
                        access_user.first_name = (
                            user_name[0] if len(user_name) > 1 else ""
                        )
                        access_user.forgot_password_hash = None
                        access_user.forgot_password_expire = None
                        access_user.is_active = response_colaborador_json["ativo"]
                        access_user.is_staff = True
                        access_user.is_superuser = False
                        access_user.last_login = None
                        access_user.last_name = (
                            user_name[1] if len(user_name) >= 2 else ""
                        )
                        access_user.partner_id = partner.id
                        access_user.password = "SEM SENHA"
                        access_user.phone_number = str(
                            location_country.idd_code
                        ) + format_phone(response_colaborador_json["telefone"])
                        access_user.username = response_colaborador_json["login"]
                        access_user.is_franchisor_user = False

                        another_user = AccessUser.objects.filter(
                            Q(username=access_user.username) & ~Q(id=access_user.id)
                        ).first()
                        if another_user:
                            access_user.username = f"{response_colaborador_json['login']}_{str(partner.id)}"

                        another_email = AccessUser.objects.filter(
                            Q(email=access_user.email) & ~Q(id=access_user.id)
                        ).first()
                        if another_email:
                            access_user.email = f"funcionario_.{response_colaborador_json['id']}@onoderapt.com.br"

                        access_user.save()

                        criaTraducaoId(
                            "funcionario",
                            response_colaborador_json["id"],
                            "access_user",
                            access_user.id,
                        )
                    else:
                        atualizaTraducaoId(
                            "funcionario",
                            response_colaborador_json["id"],
                            "access_user",
                            access_user.id,
                        )
