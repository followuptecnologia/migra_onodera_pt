import re
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
import pytz
from django.db.models import F, Sum, Case, When, Value, IntegerField


# ------------------------------------------------#
#  Get date from dmy string format               #
# ------------------------------------------------#
def date_from_dmy(dmy: str) -> str:
    if not dmy:
        return None

    try:
        if re.match(r"^\d{2}[/|-]\d{2}[/|-]\d{4}$", dmy):
            day = dmy[0:2]
            month = dmy[3:5]
            year = dmy[6:10]
            # return year + "-" + month + "-" + day
            return datetime.fromisoformat(f"{year}-{month}-{day}")

        return None

    except Exception:
        return None


# ------------------------------------------------#
#  Get date from dmy string format               #
# ------------------------------------------------#
def datetime_from_dmy(dmy: str) -> datetime:
    if not dmy:
        return None

    try:
        if re.match(r"^\d{2}[/|-]\d{2}[/|-]\d{4}\s\d{2}\:\d{2}$", dmy):
            day = dmy[0:2]
            month = dmy[3:5]
            year = dmy[6:10]
            hour = dmy[11:13]
            minute = dmy[14:16]
            second = "00"
            return datetime.fromisoformat(
                f"{year}-{month}-{day} {hour}:{minute}:{second}"
            )

        if re.match(r"^\d{2}[/|-]\d{2}[/|-]\d{4}\s\d{2}\:\d{2}\:\d{2}$", dmy):
            day = dmy[0:2]
            month = dmy[3:5]
            year = dmy[6:10]
            hour = dmy[11:13]
            minute = dmy[14:16]
            second = dmy[17:19]
            return datetime.fromisoformat(
                f"{year}-{month}-{day} {hour}:{minute}:{second}"
            )

        return None

    except Exception:
        return None


# ------------------------------------------------#
#  Get date from dmy string format               #
# ------------------------------------------------#
def datetime_tz_from_dmy(dmy: str) -> datetime:
    if not str:
        return None

    try:
        date_time = datetime_from_dmy(dmy)
        if date_time:
            return date_time.astimezone(pytz.timezone(settings.TIME_ZONE))

        return None

    except Exception:
        return None


# ------------------------------------------------#
#  Validate phone number                         #
# ------------------------------------------------#
def validate_phone_number(phone_number: str) -> bool:
    if not phone_number:
        return False

    phone_number = extract_numbers(phone_number)
    if len(phone_number) == 10 or len(phone_number) == 11:  # Somente números
        return True
    else:
        return False


# ------------------------------------------------#
#  Format CEP number                             #
# ------------------------------------------------#
def format_cep(cep) -> str:
    if cep is None:
        return ""

    cep = extract_numbers(cep)
    if cep == "":
        return ""

    cep = str(int(cep.zfill(8))).zfill(8)  # Remove zeros à esquerda

    if len(cep) > 8:
        cep = cep[0:8]

    try:
        return "%s%s%s%s%s-%s%s%s" % tuple(cep)

    except Exception:
        return ""


# ------------------------------------------------#
#  Format CPF number                             #
# ------------------------------------------------#
def format_cpf(cpf) -> str:
    if cpf is None:
        return ""

    cpf = extract_numbers(cpf)
    if cpf == "":
        return ""

    cpf = str(int(cpf.zfill(11))).zfill(11)  # Remove zeros à esquerda

    if len(cpf) > 11:
        cpf = cpf[0:11]

    try:
        return "%s%s%s.%s%s%s.%s%s%s-%s%s" % tuple(cpf)

    except Exception:
        return ""


# ------------------------------------------------#
#  Format CNPJ number                            #
# ------------------------------------------------#
def format_cnpj(cnpj) -> str:
    if not cnpj:
        return ""

    cnpj = extract_numbers(cnpj)
    cnpj = str(int(cnpj.zfill(14))).zfill(14)  # completa zeros à esquerda

    if len(cnpj) > 14:
        cnpj = cnpj[
            0:14
        ]  # remove caracteres excedentes (deve conter apenas 14 digitos)

    try:
        return "%s%s.%s%s%s.%s%s%s/%s%s%s%s-%s%s" % tuple(cnpj)

    except Exception:
        return ""


# ------------------------------------------------#
#  Format phone number                           #
# ------------------------------------------------#
def format_phone(phone_number: str) -> str:
    if not phone_number:
        return ""

    idd_code = None

    # International Direct Dialing codes
    if phone_number[0] == "+":
        idd_table = "+1,+7,+20,+27,+30,+31,+32,+33,+34,+36,+39,+40,+41,+43,+44,+45,+46,+47,+48,+49,+51,+52,+53,+54,+55,+56,+57,+58,+60,+61,+62,+63,+64,+65,+66,+81,+82,+84,+86,+90,+91,+92,+93,+94,+95,+98,+212,+213,+216,+218,+220,+221,+222,+223,+224,+225,+226,+227,+228,+229,+230,+231,+232,+233,+234,+236,+237,+238,+239,+240,+241,+242,+243,+244,+245,+246,+247,+248,+249,+250,+251,+252,+253,+254,+255,+256,+257,+258,+259,+260,+261,+262,+263,+264,+265,+266,+267,+268,+269,+281,+290,+291,+297,+298,+299,+350,+351,+352,+353,+354,+355,+356,+357,+358,+359,+370,+371,+372,+373,+374,+375,+376,+377,+378,+380,+382,+385,+386,+387,+389,+420,+421,+423,+500,+501,+502,+503,+504,+505,+506,+507,+508,+509,+590,+591,+592,+593,+594,+595,+596,+597,+598,+599,+670,+672,+673,+674,+675,+676,+677,+678,+679,+680,+681,+682,+683,+684,+685,+686,+687,+688,+689,+690,+691,+692,+833,+838,+839,+850,+852,+853,+854,+855,+856,+880,+886,+960,+961,+962,+963,+964,+965,+966,+967,+968,+970,+971,+973,+974,+975,+976,+977,+992,+993,+994,+995,+996,+998"
        idd_list = idd_table.split(",")
        for idd in idd_list:
            if idd == phone_number[0 : len(idd)]:
                idd_code = idd
                break

        if idd_code:
            phone_number = phone_number.replace(
                idd_code, ""
            )  # Clear IDD code from phone number

    #   try:
    phone_number = extract_numbers(phone_number)
    if phone_number == "":
        return ""

    if idd_code == "+55" or not idd_code:  # Brazil is the default country
        while phone_number != "" and phone_number[0] == "0":
            phone_number = phone_number[1:]

        if len(phone_number) == 11:  # Mobile phone with DDD
            phone_number = "(%s%s) %s%s%s%s%s-%s%s%s%s" % tuple(phone_number)
        elif len(phone_number) == 10:  # Landline with DDD
            phone_number = "(%s%s) %s%s%s%s-%s%s%s%s" % tuple(phone_number)
        elif len(phone_number) == 9:  # Mobile without DDD
            phone_number = "(00) %s%s%s%s%s-%s%s%s%s" % tuple(phone_number)
        elif len(phone_number) == 8:  # Landline without DDD
            phone_number = "(00) %s%s%s%s-%s%s%s%s" % tuple(phone_number)

    return phone_number


#    except Exception:
#        return ""


# ------------------------------------------------#
# Extract only numbers from a string             #
# ------------------------------------------------#
def extract_numbers(string) -> str:
    if not string:
        string = ""

    numbers_list = [int(digit) for digit in string if digit.isdigit()]

    number = ""
    for dig in numbers_list:
        number = number + str(dig)

    return str(number)


# ------------------------------------------------#
# Validate CPF                                   #
# ------------------------------------------------#
def validate_cpf(cpf) -> bool:
    """
    Efetua a validação do CPF, tanto formatação quando dígito verificadores.

    Parâmetros:
        cpf (str): CPF a ser validado

    Retorno:
        bool:
            - Falso, quando o CPF não possuir o formato 999.999.999-99;
            - Falso, quando o CPF não possuir 11 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    # >>> validate('529.982.247-25')
    True
    # >>> validate('52998224725')
    False
    # >>> validate('111.111.111-11')
    False
    """

    # Verifica a formatação do CPF
    try:
        cpf = format_cpf(cpf)
        if not re.match(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf):
            return False

        # Obtém apenas os números do CPF, ignorando pontuações
        numbers = extract_numbers(cpf)

        # Verifica se o CPF possui 11 números:
        if len(numbers) != 11:
            return False

        # Validação do primeiro dígito verificador:
        sum_of_products = 0
        for a in range(10, 1, -1):
            b = numbers[10 - a]
            sum_of_products = sum_of_products + (a * int(b))

        expected_digit = str((sum_of_products * 10 % 11) % 10)
        if numbers[9] != expected_digit:
            return False

        # Validação do segundo dígito verificador:
        sum_of_products = 0
        for a in range(11, 1, -1):
            b = numbers[11 - a]
            sum_of_products = sum_of_products + (a * int(b))

        expected_digit = str((sum_of_products * 10 % 11) % 10)
        if numbers[10] != expected_digit:
            return False

        return True
    except Exception:
        return False


# -----------------------------------------
# Returns a set of dates between two dates
# -----------------------------------------
def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


# -----------------------------------------
# Remove HTML tags from text
# -----------------------------------------
def remove_html_tags(html_content):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", html_content)
    return cleantext


# -----------------------------------------
# Adiciona minutos a uma determinada hora
# -----------------------------------------
def add_minutes(time, minutes) -> str:
    if re.match(r"^\d{2}[:]\d{2}[:]\d{2}$", time):
        h = int(time.split(":")[0])
        m = int(time.split(":")[1])
        s = int(time.split(":")[2])
        total = s + (m * 60) + (h * 60 * 60)
        total += minutes * 60
        m = int(total / 60)
        s = total - (m * 60)
        h = int(m / 60)
        m = m - (h * 60)
        h = h % 24
        return "{:02d}".format(h) + ":" + "{:02d}".format(m) + ":" + "{:02d}".format(s)
    else:
        return None


from apps.migrate.onodera.save.models import (
    LegacyTranslateId,
    SalesOrderSkuBalance,
    SalesOrderSku,
    AccessUser,
    ScheduleSkuResource,
    Schedule,
    ScheduleStatus,
)
from apps import parametros


def ifNone(ref, replace_value):
    if ref is None:
        return replace_value
    else:
        return ref


def criaTraducaoId(
    legacy_table: str,
    legacy_id,
    gester_table: str,
    gester_id,
    corporate_group_unity_id=None,
    corporate_group_id=parametros.corporate_group_id,
):
    # id_ant = leTraducaoId(legacy_table,legacy_id,gester_table,corporate_group_unity_id,corporate_group_id)
    #
    # if id_ant is not None:
    #     raise RuntimeError(f"Duplicated key writting leTraducaoId ({legacy_table} {legacy_id} {gester_table} {corporate_group_unity_id} {corporate_group_id})")
    #     exit(-1)
    #
    # try:
    #     obj = LegacyTranslateId.objects.latest('id')
    #     id_trad = obj.id + 1
    #
    # except:
    #     id_trad = 1

    legacy_translate_id = LegacyTranslateId()
    # legacy_translate_id.id = id_trad
    legacy_translate_id.is_active = True
    legacy_translate_id.is_template = False
    legacy_translate_id.legacy_table = legacy_table
    legacy_translate_id.legacy_id = legacy_id
    legacy_translate_id.gester_table = gester_table
    legacy_translate_id.gester_id = gester_id
    legacy_translate_id.corporate_group_id = corporate_group_id
    legacy_translate_id.corporate_group_unity_id = corporate_group_unity_id
    legacy_translate_id.created_on = datetime.now().astimezone()
    legacy_translate_id.last_edit_on = datetime.now().astimezone()
    legacy_translate_id.save(force_insert=True)


def atualizaTraducaoId(
    legacy_table: str,
    legacy_id,
    gester_table: str,
    gester_id,
    corporate_group_unity_id=None,
    corporate_group_id=parametros.corporate_group_id,
):
    legacy_translate_id = LegacyTranslateId.objects.filter(
        legacy_table=legacy_table,
        legacy_id=legacy_id,
        gester_table=gester_table,
        corporate_group_id=corporate_group_id,
        corporate_group_unity_id=corporate_group_unity_id,
    ).first()
    if legacy_translate_id:
        legacy_translate_id.gester_id = gester_id
        legacy_translate_id.last_edit_on = datetime.now().astimezone()
        legacy_translate_id.save(force_update=True)
    else:
        criaTraducaoId(legacy_table, legacy_id, gester_table, gester_id)


def leTraducaoId(
    legacy_table: str,
    legacy_id,
    gester_table: str,
    corporate_group_unity_id=None,
    corporate_group_id=parametros.corporate_group_id,
):
    try:
        legacy_translate_id = LegacyTranslateId.objects.filter(
            legacy_table=legacy_table,
            legacy_id=legacy_id,
            gester_table=gester_table,
            corporate_group_id=corporate_group_id,
            corporate_group_unity_id=corporate_group_unity_id,
        ).first()
        if legacy_translate_id:
            return legacy_translate_id.gester_id
        else:
            return None

    # except LegacyTranslateId.DoesNotExist:
    #     return None

    except:
        return None


def traducaoUsuario(legacy_user_id):
    if legacy_user_id is not None:
        access_user_id = leTraducaoId("funcionario", legacy_user_id, "access_user")
        access_user = AccessUser.objects.filter(id=access_user_id).first()
        return access_user.id if access_user else 1

    return None


def traducaoUsuarioVenda(legacy_user_id):
    if legacy_user_id is not None:
        return leTraducaoId("funcionario", legacy_user_id, "access_user")

    return None


def get_last_migration(corporate_group_unity_id: int, table_name: str) -> datetime:
    from apps.migrate.onodera.save.models import LegacyMigrationStatus

    last_migration_on = "1901-01-01 00:00:00+0000"

    legacy_migration_status = LegacyMigrationStatus.objects.filter(
        legacy_unity_id=corporate_group_unity_id, legacy_table_name=table_name
    ).first()
    if legacy_migration_status:
        last_migration_on = legacy_migration_status.last_migration_on
    else:
        legacy_migration_status = LegacyMigrationStatus()
        legacy_migration_status.legacy_unity_id = corporate_group_unity_id
        legacy_migration_status.legacy_table_name = table_name
        legacy_migration_status.last_migration_on = last_migration_on
        legacy_migration_status.save()

    return last_migration_on


def set_last_migration(
    corporate_group_unity_id: int, table_name: str, last_update_on: datetime
):
    if last_update_on == None:
        return

    from apps.migrate.onodera.save.models import LegacyMigrationStatus

    legacy_migration_status = LegacyMigrationStatus.objects.filter(
        legacy_unity_id=corporate_group_unity_id, legacy_table_name=table_name
    ).first()

    if legacy_migration_status:
        if (
            legacy_migration_status.last_migration_on is None
            or legacy_migration_status.last_migration_on < last_update_on
        ):
            legacy_migration_status.last_migration_on = last_update_on
            legacy_migration_status.save()

    return


def insert_balance(
    created_on,
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
        created_on=created_on,
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


def list_customer_sku_balance(customer_id, unit, sales_order=None):
    if sales_order:
        sales_order_sku_balance = SalesOrderSkuBalance.objects.filter(
            sales_order_sku__sales_order=sales_order,
        )
    else:
        sales_order_sku_balance = SalesOrderSkuBalance.objects.filter(
            sales_order_sku__sales_order__customer_partner_id=customer_id,
            sales_order_sku__sales_order__corporate_group_unity_id=unit,
        ).exclude(
            sales_order_sku__sales_order__order_status__in=[
                "canceledSale",
                "budget",
                "invalid",
                "sale",
            ]
        )

    balances = (
        sales_order_sku_balance.values(
            "sales_order_sku", "sales_order_sku__quantity_sold"
        )
        .annotate(
            quantity_available_schedule=(
                Sum(
                    Case(
                        When(reason_type="entry", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                + Sum(
                    Case(
                        When(reason_type="scheduling_cancelled", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="scheduling", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="discount", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            ),
            balance_customer=(
                Sum(
                    Case(
                        When(reason_type="entry", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                + Sum(
                    Case(
                        When(reason_type="execution_cancelled", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="execution", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="discount", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            ),
            quantity_used=(
                Sum(
                    Case(
                        When(reason_type="execution", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="execution_cancelled", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
            ),
            quantity_scheduled=(
                Sum(
                    Case(
                        When(reason_type="scheduling", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - Sum(
                    Case(
                        When(reason_type="scheduling_cancelled", then=F("quantity")),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                )
                - F("quantity_used")
            ),
            quantity_desconted=Sum(
                Case(
                    When(reason_type="discount", then=F("quantity")),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ),
            quantity_total_used=F("quantity_used")
            + F("quantity_scheduled")
            + F("quantity_desconted"),
            quantity_effective_used=F("quantity_used") + F("quantity_desconted"),
        )
        .order_by()
    )

    return balances


def balance_sku(sales_order_sku_id):
    sales_order_sku = SalesOrderSku.objects.get(id=sales_order_sku_id)
    return next(
        (
            sku_balance
            for sku_balance in list_customer_sku_balance(
                customer_id=None,
                unit=sales_order_sku.sales_order.corporate_group_unity_id,
                sales_order=sales_order_sku.sales_order,
            )
            if sku_balance["sales_order_sku"] == sales_order_sku.id
        ),
        None,
    )


def insert_balance_sku(
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


def recalcula_saldo(sales):
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
            else (
                "Demonstração adquirida"
                if sales.order_status == "demonstration"
                else "Reposição adquirida"
            )
        )
        insert_balance_sku(
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
                insert_balance_sku(
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
                    else (
                        "Status alterado para Faltou"
                        if "missed" in schedule_status
                        else "Status alterado para Faltou Confirmado"
                    )
                )
                insert_balance_sku(
                    "scheduling",
                    "exit",
                    sales_sku.id,
                    1,
                    "Serviço agendado",
                    "",
                    schedule.id,
                )
                insert_balance_sku(
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
                insert_balance_sku(
                    "scheduling",
                    "exit",
                    sales_sku.id,
                    1,
                    "Serviço agendado",
                    "",
                    schedule.id,
                )
                insert_balance_sku(
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
            insert_balance_sku(
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
            insert_balance_sku(
                "discount", "exit", sales_sku.id, quantity, "Venda cancelada", ""
            )
            sales_sku.quantity_desconted += quantity
            sales_sku.save()

        ## SESSÃO UTILIZADA NO SISTEMA ANTERIOR ##
        if sales_sku.quantity_used_other_systems > 0:
            insert_balance_sku(
                "scheduling",
                "exit",
                sales_sku.id,
                sales_sku.quantity_used_other_systems,
                "Serviço agendado",
                "Agendamento realizado no sistema anterior",
            )
            insert_balance_sku(
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
