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
    atualizaTraducaoId,
    ifNone,
    format_phone,
    format_cep,
)
from apps import parametros
from apps.migrate.onodera.save.models import (
    CorporateGroupUnity,
    Partner,
    PartnerUnityCustomer,
    CrmMedia,
    LocationCity,
    LocationState,
    LocationCountry,
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
data = {
    "dataDe": "",
    "dataAte": "",
    "dataCadastroDe": "",
    "dataCadastroAte": "",
    "isCliente": "true",
    "isExCliente": "true",
    "isProspect": "true",
    "modeloRelatorio": "1",
    "e": f"{parametros.nomefilial_sw}",
}
url = "http://onoderapt.swerp.com.br/api/relatorios/Cliente_ListagemCliente/?j={%22dataDe%22:%22%22,%22dataAte%22:%22%22,%22dataCadastroDe%22:%22%22,%22dataCadastroAte%22:%22%22,%22isCliente%22:true,%22isExCliente%22:true,%22isProspect%22:true,%22modeloRelatorio%22:%221%22,%22e%22:%22Braga%22}"

# LISTA TODOS OS CLIENTES ATRAVES DO RELATORIO #
response = requests.get(url=url, data=json.dumps(data), headers=headers)
clientes_relatorio_json = response.json()

### PERCORRENDO TODOS OS CADASTROS DA LISTA ###
quant_total = len(clientes_relatorio_json)
percent_ant = None
quant_lida = 0
print("TOTAL: ", quant_total)
for cliente_relatorio_json in clientes_relatorio_json:
    quant_lida += 1
    percent = int((quant_lida / quant_total) * 100)
    if percent != percent_ant:
        percent_ant = percent
        print("\r", f"Lido: {percent}%", end="")
        if quant_lida == quant_total:
            print("")

    # FILTRA O CLIENTE PELO O NOME #
    data_list = {"nome": f"{cliente_relatorio_json['nomePessoa']}", "documento": "", "numeroVenda": "",
                 "telefone": "", "email": "",
                 "situacao": ["1", "2", "3", "4"], "Top50": 'false'}
    url_list = 'http://onoderapt.swerp.com.br/api/clientes/lista'

    response_list = requests.post(url=url_list, data=json.dumps(data_list), headers=headers)
    clientes_json = response_list.json()

    for cliente_json in clientes_json:

        url_get = "http://onoderapt.swerp.com.br/api/clientes/getClienteById?id=" + str(
            cliente_json["id"]
        )
        response_get = requests.get(url=url_get, headers=headers)

        if response_get.status_code == 200:
            with transaction.atomic(using="gester"):
                response_cliente_json = response_get.json()
                sexo: str
                if (
                        response_cliente_json["nomePessoa"] is not None
                        and len(response_cliente_json["nomePessoa"].strip()) > 0
                ):
                    if response_cliente_json["sexo"] == "F":
                        sexo = "female"
                    elif response_cliente_json["sexo"] == "M":
                        sexo = "male"
                    else:
                        sexo = ""

                    other_unity = None
                    partner = None
                    partner_id = leTraducaoId(
                        "pessoa", response_cliente_json["id"], "partner"
                    )
                    partner = Partner.objects.filter(id=partner_id).first()

                    if partner is None:
                        acao = "criado"
                    else:
                        acao = "atualizado"
                        other_unity = PartnerUnityCustomer.objects.filter(
                            partner_id=partner.id
                        ).exclude(corporate_group_unity_id=corporate_group_unity.id)

                    if partner is None or parametros.update_if_exists:
                        location_city = LocationCity.objects.filter(
                            name=response_cliente_json["municipio"]
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

                        estado_civil = ""
                        if response_cliente_json["estadoCivil"] == 0:
                            estado_civil = ""
                        elif response_cliente_json["estadoCivil"] == 1:
                            estado_civil = "married"
                        elif response_cliente_json["estadoCivil"] == 2:
                            estado_civil = "separated"
                        elif response_cliente_json["estadoCivil"] == 3:
                            estado_civil = "single"
                        elif response_cliente_json["estadoCivil"] == 4:
                            estado_civil = "married"  # União estável
                        elif response_cliente_json["estadoCivil"] == 5:
                            estado_civil = "widowed"

                        # MÍDIA NO GESTER
                        if response_cliente_json["origemMedia"] is not None:
                            crm_media_id = leTraducaoId(
                                "origem_media",
                                response_cliente_json["origemMedia"],
                                "crm_media",
                                corporate_group_unity.id,
                            )
                            crm_media = CrmMedia.objects.filter(id=crm_media_id)
                            if crm_media.count() > 0:
                                crm_media_id = crm_media.first()
                            else:
                                crm_media_id = None
                        else:
                            crm_media_id = None

                        ### CRIA REGISTRO DA TABELA PARTNER NO GESTER ###
                        created = False
                        if partner is None:
                            partner = Partner()
                            created = True

                        if not created and other_unity is not None:
                            partner_unity_customer = (
                                PartnerUnityCustomer.objects.filter(
                                    partner_id=partner.id,
                                    corporate_group_unity_id=corporate_group_unity.id,
                                ).first()
                            )
                            atualizaTraducaoId(
                                "pessoa",
                                response_cliente_json["id"],
                                "partner",
                                partner.id,
                            )
                            if not partner_unity_customer:
                                partner_unity_customer = PartnerUnityCustomer()
                                partner_unity_customer.created_on = ifNone(
                                    partner.created_on, datetime.now()
                                )
                                partner_unity_customer.last_edit_on = (
                                    partner.last_edit_on
                                )
                                partner_unity_customer.created_by_id = (
                                    partner.created_by_id
                                )
                                partner_unity_customer.last_edit_by_id = (
                                    partner.last_edit_by_id
                                )
                                partner_unity_customer.created_on = (
                                    response_cliente_json["dataCriacao"]
                                )
                                partner_unity_customer.last_edit_on = (
                                    response_cliente_json["dataCriacao"]
                                )
                                partner_unity_customer.is_template = False
                                partner_unity_customer.partner_id = partner.id
                                partner_unity_customer.customer_id = partner.id
                                partner_unity_customer.corporate_group_id = (
                                    parametros.corporate_group_id
                                )
                                partner_unity_customer.corporate_group_unity_id = (
                                    corporate_group_unity.id
                                )

                                partner_unity_customer.is_active = (
                                    True
                                    if response_cliente_json["situacao"] != 5
                                    else False
                                )
                                partner.main_unit_id = corporate_group_unity.id
                                partner.customer_corporate_unity_id = (
                                    corporate_group_unity.id
                                )
                                partner.is_customer = True
                                partner.save()
                                partner_unity_customer.save()
                            continue

                        if response_cliente_json["nomePessoa"] is not None:
                            pessoa_nomes = response_cliente_json["nomePessoa"].split(
                                " ", 1
                            )
                        else:
                            pessoa_nomes = []

                        partner.whatsapp_integration_code = ""
                        partner.created_on = ifNone(
                            response_cliente_json["dataCriacao"], datetime.now()
                        )
                        partner.last_edit_on = response_cliente_json["dataCriacao"]
                        partner.created_by_id = 1
                        partner.last_edit_by_id = 1
                        partner.is_active = True
                        partner.is_template = False
                        partner.name = ifNone(response_cliente_json["nomePessoa"], "")
                        partner.first_name = (
                            pessoa_nomes[0] if len(pessoa_nomes) >= 1 else ""
                        )
                        partner.last_name = (
                                                pessoa_nomes[1] if len(pessoa_nomes) >= 2 else ""
                                            )[:70]
                        partner.login_name = ""
                        partner.password = "SEM SENHA"
                        partner.person_type = (
                            "natural"
                            if response_cliente_json["tipoPessoa"] == "1"
                            else "legal"
                        )
                        partner.federal_tax_number = response_cliente_json["cpf"]
                        partner.state_tax_number = ""
                        partner.city_tax_number = ""
                        partner.federal_register_number = ""
                        partner.identity_card_number = ""
                        partner.birth_date = (
                            datetime.strptime(
                                response_cliente_json["dataNascimento"], "%d/%m/%Y"
                            ).strftime("%Y-%m-%d")
                            if response_cliente_json["dataNascimento"]
                               and response_cliente_json["dataNascimento"] != ""
                            else None
                        )
                        partner.genre = sexo
                        partner.mobile = format_phone(response_cliente_json["celular"])[
                                         :20
                                         ]
                        partner.phone = format_phone(response_cliente_json["telefone"])[
                                        :20
                                        ]
                        partner.business_phone = format_phone(
                            response_cliente_json["telefoneComercial"]
                        )[:20]
                        partner.whatsapp_number = format_phone(
                            response_cliente_json["celular"]
                        )[:20]
                        partner.trade_name = ""
                        partner.marital_status = estado_civil
                        partner.email = ifNone(response_cliente_json["email"], "")
                        partner.schedule_notification_mail = False
                        partner.schedule_notification_whatsapp = False
                        partner.schedule_notification_sms = False
                        partner.customer_responsible_name = ""
                        partner.customer_responsible_legal_id = None
                        partner.is_customer = True
                        partner.is_supplier = (
                            False
                            if partner.is_supplier is None
                            else partner.is_supplier
                        )
                        partner.is_employee = (
                            False
                            if partner.is_employee is None
                            else partner.is_employee
                        )
                        partner.is_user = (
                            False if partner.is_user is None else partner.is_user
                        )
                        partner.is_corporate_unity = (
                            False
                            if partner.is_corporate_unity is None
                            else partner.is_corporate_unity
                        )
                        partner.is_unity_owner = (
                            False
                            if partner.is_unity_owner is None
                            else partner.is_unity_owner
                        )
                        partner.is_professional = (
                            False
                            if partner.is_professional is None
                            else partner.is_professional
                        )
                        partner.investor_only = False
                        partner.work_card = None
                        partner.serial_number = None
                        partner.pis = None
                        partner.transportation_voucher = (
                            ""
                            if partner.transportation_voucher is None
                            else partner.transportation_voucher
                        )
                        partner.meal_voucher = (
                            "" if partner.meal_voucher is None else partner.meal_voucher
                        )
                        partner.other_voucher = (
                            ""
                            if partner.other_voucher is None
                            else partner.other_voucher
                        )
                        partner.bank = ""
                        partner.agency = ""
                        partner.checking_account = ""
                        partner.foreign_tax_number = response_cliente_json["rg"]
                        partner.issuing_agency = (
                            ""
                            if partner.issuing_agency is None
                            else partner.issuing_agency
                        )
                        partner.receive_email = True
                        partner.receive_sms = True
                        partner.receive_whats = True
                        partner.description = ""
                        partner.classification = (
                            ""
                            if partner.classification is None
                            else partner.classification
                        )
                        partner.customer_code = (
                            None
                            if partner.customer_code is None
                            else partner.customer_code
                        )
                        partner.cell_phone_operator = (
                            ""
                            if partner.cell_phone_operator is None
                            else partner.cell_phone_operator
                        )
                        partner.point_registry = (
                            False
                            if partner.point_registry is None
                            else partner.point_registry
                        )
                        partner.corporate_group_id = parametros.corporate_group_id
                        partner.customer_corporate_unity_id = None
                        partner.customer_last_attendant_unity_id = None
                        partner.main_unit_id = None
                        partner.media_id = crm_media_id.id if crm_media_id else ""
                        partner.referral_customer_id = None
                        partner.supplier_corporate_unity_id = None
                        partner.type_media_id = (
                            crm_media_id.media_group_id if crm_media_id else ""
                        )
                        partner.federal_tax_document_type_id = None
                        partner.federal_register_document_type_id = None
                        partner.foreign_tax_document_type_id = None
                        partner.occupation = ""
                        partner.employee_salary = (
                            0
                            if partner.employee_salary is None
                            else partner.employee_salary
                        )
                        partner.customer_id = 0
                        partner.classification = "new"
                        partner.have_federal_tax_number = (
                            True if partner.federal_tax_number != "" else False
                        )
                        partner.location_country_id = (
                            location_country.id if location_country else None
                        )

                        if partner.phone != "" and not partner.phone.startswith(
                                str(location_country.idd_code)
                        ):
                            partner.phone = (
                                    "+" + str(location_country.idd_code) + partner.phone
                            )
                        if (
                                partner.business_phone != ""
                                and not partner.business_phone.startswith(
                            str(location_country.idd_code)
                        )
                        ):
                            partner.business_phone = (
                                    "+"
                                    + str(location_country.idd_code)
                                    + partner.business_phone
                            )
                        if partner.mobile != "" and not partner.mobile.startswith(
                                str(location_country.idd_code)
                        ):
                            partner.mobile = (
                                    "+" + str(location_country.idd_code) + partner.mobile
                            )
                        if (
                                partner.whatsapp_number != ""
                                and not partner.whatsapp_number.startswith(
                            str(location_country.idd_code)
                        )
                        ):
                            partner.whatsapp_number = (
                                    "+"
                                    + str(location_country.idd_code)
                                    + partner.whatsapp_number
                            )

                        if partner.federal_tax_number is None:
                            partner.customer_type = Partner.LEAD_CUSTOMER

                        if partner.federal_tax_number and partner.location_city:
                            partner.customer_type = Partner.REGISTERED_CUSTOMER

                        partner.address = ifNone(response_cliente_json["endereco"], "")
                        partner.address_number = ifNone(
                            response_cliente_json["numero"], ""
                        )
                        partner.address_neighborhood = ifNone(
                            response_cliente_json["bairro"], ""
                        )
                        partner.address_complement = ifNone(
                            response_cliente_json["complemento"], ""
                        )
                        partner.zip_code = format_cep(response_cliente_json["cep"])
                        partner.location_country_id = (
                            location_country.id
                            if location_country
                            else parametros.location_country_id
                        )
                        partner.location_state_id = (
                            location_state.id if location_state else ""
                        )
                        partner.location_city_id = (
                            location_city.id if location_city else ""
                        )
                        partner.save()

                    if partner_id is None:
                        criaTraducaoId(
                            "pessoa", response_cliente_json["id"], "partner", partner.id
                        )
                    else:
                        atualizaTraducaoId(
                            "pessoa", response_cliente_json["id"], "partner", partner.id
                        )

                    partner_unity_customer = None
                    partner_unity_customer = PartnerUnityCustomer.objects.filter(
                        partner_id=partner.id,
                        corporate_group_unity_id=corporate_group_unity.id,
                    ).first()

                    if not partner_unity_customer:
                        acao = "criado"
                    else:
                        acao = "atualizado"

                    if partner_unity_customer is None or parametros.update_if_exists:
                        if not partner_unity_customer:
                            partner_unity_customer = PartnerUnityCustomer()
                            partner_unity_customer.created_on = ifNone(
                                partner.created_on, datetime.now()
                            )
                            partner_unity_customer.last_edit_on = partner.last_edit_on
                            partner_unity_customer.created_by_id = partner.created_by_id
                            partner_unity_customer.last_edit_by_id = (
                                partner.last_edit_by_id
                            )
                            partner_unity_customer.created_on = response_cliente_json[
                                "dataCriacao"
                            ]
                            partner_unity_customer.last_edit_on = response_cliente_json[
                                "dataCriacao"
                            ]
                            partner_unity_customer.is_template = False
                            partner_unity_customer.partner_id = partner.id
                            partner_unity_customer.customer_id = partner.id
                            partner_unity_customer.corporate_group_id = (
                                parametros.corporate_group_id
                            )
                            partner_unity_customer.corporate_group_unity_id = (
                                corporate_group_unity.id
                            )
                            partner_unity_customer.is_active = True
                            partner.main_unit_id = corporate_group_unity.id
                            partner.customer_corporate_unity_id = (
                                corporate_group_unity.id
                            )
                            partner.save()
                            partner_unity_customer.save()

## ATUALIZA customer_code ###
unity = CorporateGroupUnity.objects.filter(id=corporate_group_unity.id).first()

if unity:
    customers_unity = PartnerUnityCustomer.objects.filter(
        corporate_group_unity_id=unity.id
    ).order_by("created_on")
    total = customers_unity.count()
    percent_ant = None
    quant_lida = 0
    print("\r")
    print("--- UNIDADE {0} ---".format(unity.abbreviated_name))
    print("TOTAL: ", total)

    unity.customer_id_next_value = 0
    unity.save()

    for customer_unity in customers_unity:
        quant_lida += 1
        percent = round((quant_lida / total) * 100)
        if percent != percent_ant:
            percent_ant = percent
            print("\r", f"Lido: {percent}%", end="")
            if quant_lida == total:
                print("")

        unity.customer_id_next_value += 1
        unity.save()
        customer = Partner.objects.filter(id=customer_unity.partner_id).first()
        if not customer:
            continue
        customer.customer_code = str(unity.customer_id_next_value)
        customer.save()

print(colored("SCRIPT FINALIZADO ;-)", "green", None, attrs=["bold"]))
