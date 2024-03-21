# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.db.models import CASCADE, TextField, RESTRICT


class AccessPermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    code = models.CharField(max_length=255)
    frontend_code = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(
        "AccessPermissionCategory", models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_permission"
        unique_together = (("corporate_group", "is_template", "is_active", "code"),)


class AccessPermissionCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    label = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_permission_category"


class AccessProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=255)
    is_base = models.BooleanField()
    base_profile = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    original_corporate_group_unity = models.ForeignKey(
        "CorporateGroupUnity", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_profile"


class AccessProfileCorporateGroupUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    access_profile = models.ForeignKey(AccessProfile, models.DO_NOTHING)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey("CorporateGroupUnity", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_profile_corporate_group_unity"
        unique_together = (
            ("corporate_group", "access_profile", "corporate_group_unity"),
        )


class AccessProfilePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    is_granted = models.BooleanField()
    can_grant = models.BooleanField()
    can_see = models.BooleanField()
    access_permission = models.ForeignKey(AccessPermission, models.DO_NOTHING)
    access_profile = models.ForeignKey(AccessProfile, models.DO_NOTHING)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_profile_permission"
        unique_together = (("corporate_group", "access_profile", "access_permission"),)


class AccessUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    email = models.CharField(unique=True, max_length=254)
    phone_number = models.CharField(max_length=20)
    is_staff = models.BooleanField()
    forgot_password_hash = models.CharField(max_length=255, blank=True, null=True)
    forgot_password_expire = models.DateTimeField(blank=True, null=True)
    accepted_terms = models.BooleanField()
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    current_unity = models.ForeignKey(
        "CorporateGroupUnity", models.DO_NOTHING, blank=True, null=True
    )
    partner = models.OneToOneField("Partner", models.DO_NOTHING)
    is_franchisor_user = models.BooleanField()

    class Meta:
        managed = False
        db_table = "access_user"


class AccessUserCrmCampaignRead(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey("CrmCampaign", models.DO_NOTHING)
    user = models.ForeignKey(AccessUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "access_user_crm_campaign_read"


class AccessUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    accessuser = models.ForeignKey(AccessUser, models.DO_NOTHING)
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = "access_user_groups"
        unique_together = (("accessuser", "group_id"),)


class AccessUserPreference(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    scope = models.CharField(max_length=10)
    view_name = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    value = models.JSONField()
    access_user = models.ForeignKey(AccessUser, models.DO_NOTHING)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "access_user_preference"
        unique_together = (("access_user", "scope", "view_name", "name"),)


class AccessUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    accessuser = models.ForeignKey(AccessUser, models.DO_NOTHING)
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = "access_user_user_permissions"
        unique_together = (("accessuser", "permission_id"),)


class Acquirer(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    remainder_division_installment = models.CharField(max_length=20)
    minimum_remuneration_amount = models.DecimalField(max_digits=6, decimal_places=2)
    subtract_fee_from_installment = models.BooleanField()
    days_first_due_date = models.IntegerField()
    days_between_credit_payment = models.IntegerField()
    debit_rate = models.DecimalField(max_digits=6, decimal_places=2)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_account = models.ForeignKey("FinanceAccount", models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "acquirer"


class AcquirerCreditRate(models.Model):
    id = models.BigAutoField(primary_key=True)
    parcel = models.IntegerField()
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    acquirer = models.ForeignKey(Acquirer, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "acquirer_credit_rate"


class AcquirerFlag(models.Model):
    id = models.BigAutoField(primary_key=True)
    use_acquirer_rates = models.BooleanField()
    use_acquirer_days = models.BooleanField()
    days_first_due_date = models.IntegerField()
    days_between_credit_payment = models.IntegerField()
    debit_rate = models.DecimalField(max_digits=6, decimal_places=2)
    acquirer = models.ForeignKey(Acquirer, models.DO_NOTHING)
    flag = models.ForeignKey("CardFlag", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "acquirer_flag"


class AcquirerFlagCreditRate(models.Model):
    id = models.BigAutoField(primary_key=True)
    parcel = models.IntegerField()
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    acquirer_flag = models.ForeignKey(AcquirerFlag, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "acquirer_flag_credit_rate"


class AttendanceBehavior(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey("CorporateGroupUnity", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "attendance_behavior"


class AttendanceSensitivity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey("CorporateGroupUnity", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "attendance_sensitivity"


class CardFlag(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=100)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "card_flag"


class CashInformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    transaction_type = models.CharField(max_length=45)
    informed = models.DecimalField(max_digits=18, decimal_places=2)
    calculated = models.DecimalField(max_digits=18, decimal_places=2)
    cash_register = models.ForeignKey("CashRegister", models.DO_NOTHING)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_payment_option = models.ForeignKey(
        "FinancePaymentOption", models.DO_NOTHING
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "cash_information"


class CashRegister(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    status = models.CharField(max_length=120)
    opened_at = models.DateField()
    confered_at = models.DateField(blank=True, null=True)
    initial_balance = models.DecimalField(max_digits=18, decimal_places=2)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    confered_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey("CorporateGroupUnity", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    operator = models.ForeignKey(AccessUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "cash_register"


class CashbackHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    value = models.DecimalField(max_digits=18, decimal_places=2)
    cashback_id = models.BigIntegerField()
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_order = models.ForeignKey("SalesOrder", models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "cashback_history"


class CoreConfiguration(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    system_title = models.CharField(max_length=100)
    allows_self_subscription = models.BooleanField()
    max_corporate_groups = models.IntegerField()
    max_units_per_corporate_group = models.IntegerField()
    whatsapp_api_url = models.CharField(max_length=255)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    template_corporate_group = models.ForeignKey(
        "CorporateGroup", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_configuration"


class CoreFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    description = models.CharField(max_length=50)
    folder = models.CharField(max_length=500)
    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=100)
    type = models.CharField(max_length=30)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_file"


class CoreOccupation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_occupation"


class CoreText(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    purpose = models.CharField(max_length=50)
    text = models.CharField(max_length=200)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "core_text"


class CorporateGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    customer_id_control_type = models.CharField(max_length=30)
    scheduler_user_assignment = models.CharField(max_length=50)
    multiple_services_per_schedule = models.BooleanField()
    requires_discount_reason = models.BooleanField()
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    logo_image = models.OneToOneField(
        CoreFile, models.DO_NOTHING, blank=True, null=True
    )
    master_corporate_group_unity = models.ForeignKey(
        "CorporateGroupUnity", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "corporate_group"


class CorporateGroupUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    type = models.CharField(max_length=30)
    abbreviated_name = models.CharField(max_length=20)
    opening_date = models.DateField(blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    has_parking_for_customers = models.BooleanField()
    has_wifi_for_customers = models.BooleanField()
    has_tv_for_customers = models.BooleanField()
    has_ease_for_people_with_disability = models.BooleanField()
    is_visible_on_app = models.BooleanField()
    website_url = models.CharField(max_length=255)
    customer_id_next_value = models.IntegerField()
    timezone = models.CharField(max_length=100)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    parent_corporate_group_unity = models.ForeignKey(
        "self", models.DO_NOTHING, blank=True, null=True
    )
    partner = models.OneToOneField("Partner", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "corporate_group_unity"


class CorporateGroupUnityOpeningHour(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    status = models.CharField(max_length=10)
    type = models.CharField(max_length=20)
    weekday = models.CharField(max_length=1)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "corporate_group_unity_opening_hour"
        unique_together = (
            (
                "corporate_group",
                "corporate_group_unity",
                "status",
                "type",
                "weekday",
                "date",
            ),
        )


class CorporateGroupUnityParameterization(models.Model):
    BRL = "BRL"
    EUR = "EUR"
    CURRENCY_CHOICES = [
        (BRL, "Real (BRL)"),
        (EUR, "Euro (EUR)"),
    ]

    BEFORE_ATTENDANCE = "before_attendance"
    AFTER_ATTENDANCE = "after_attendance"
    SCHEDULE_CHECK_IN_CHOICES = [
        (BEFORE_ATTENDANCE, "Anterior ao atendimento"),
        (AFTER_ATTENDANCE, "Posterior ao atendimento"),
    ]

    SEQUENTIAL = "sequential"
    RANDOM = "random"
    MANUAL = "manual"
    CRM_LEAD_DISTRIBUTION_TYPE_CHOICES = [
        (SEQUENTIAL, "Sequencial  (Ordem de id de colaborador)"),
        (RANDOM, "Randômica (sorteio)"),
        (MANUAL, "Manual"),
    ]
    CRM_CUSTOMER_DISTIBUTION_TYPE_CHOICES = [
        (SEQUENTIAL, "Sequencial  (Ordem de id de colaborador)"),
        (RANDOM, "Randômica (sorteio)"),
        (MANUAL, "Manual"),
    ]

    FEDERAL_TAX_NUMBER = "federal_tax_number"
    SERVICE = "service"
    CONTRACT = "contract"
    CRM_RENOVATION_TYPE_CHOICES = [
        (FEDERAL_TAX_NUMBER, "CPF"),
        (SERVICE, "Serviço"),
        (CONTRACT, "Contrato"),
    ]

    ACTUAL_DAY = "actual_day"
    ON_SUNDAY = "on_sunday"
    START_WEEK_CHOICES = [
        (ACTUAL_DAY, "Dia atual"),
        (ON_SUNDAY, "No domingo"),
    ]

    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    currency = models.CharField(
        max_length=4,
        choices=CURRENCY_CHOICES,
        default=BRL,
        verbose_name="Moeda",
        help_text="Moeda usada pela unidade",
    )
    corporate_group_unity = models.ForeignKey(
        CorporateGroupUnity,
        verbose_name="Unidade",
        help_text="Unidade do Grupo Corporatívo",
        on_delete=RESTRICT,
    )
    schedule_limit_partial_sale = models.IntegerField(default=0, blank=True, null=True)
    schedule_check_in_signature = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHECK_IN_CHOICES,
        default=AFTER_ATTENDANCE,
        verbose_name="Define em que ordem deve ser preenchida a assinatura em atendimentos",
    )
    allow_evaluation_selection = models.BooleanField(
        verbose_name="Permitir seleção de avaliação", default=False
    )
    allow_packages_sale = models.BooleanField(
        verbose_name="Permitir venda de pacotes", default=False
    )
    allow_pre_sale = models.BooleanField(
        verbose_name="Permitir pré-venda", default=False
    )
    allow_ending_pre_sale_service = models.BooleanField(
        verbose_name="Permitir finalizar atendimento do tipo de pré-venda",
        default=False,
    )
    allow_scheduling_through_time_reservation = models.BooleanField(
        verbose_name="Permitir agendamento através da reserva de horário", default=False
    )
    allow_transfers_contract_customer = models.BooleanField(
        verbose_name="Permitir transferências de contrato entre clientes", default=False
    )
    allow_transfers_contract_unity = models.BooleanField(
        verbose_name="Permitir transferências de contrato entre unidades", default=False
    )
    allow_transfers_balance_customer = models.BooleanField(
        verbose_name="Permitir transferências de saldos entre clientes", default=False
    )
    allow_transfers_balance_unity = models.BooleanField(
        verbose_name="Permitir transferências de saldos entre unidades", default=False
    )
    allow_transfers_credit_customer = models.BooleanField(
        verbose_name="Permitir transferências de créditos entre clientes", default=False
    )
    allow_transfers_credit_unity = models.BooleanField(
        verbose_name="Permitir transferências de créditos entre unidades", default=False
    )
    allow_schedule_multiple_services = models.BooleanField(
        verbose_name="Permitir agendar múltiplos serviços em um agendamento",
        default=False,
    )
    show_rooms = models.BooleanField(verbose_name="Exibir Salas", default=True)

    billing_lock_day = models.IntegerField(
        default=5, null=False, verbose_name="data padrão de vencimento"
    )
    single_sale_expiration_days = models.IntegerField(
        default=30, verbose_name="Dias para o vencimento de contratos avulsos"
    )
    partner = models.ForeignKey(
        "Partner", verbose_name="Partner", on_delete=RESTRICT, null=True, blank=True
    )
    signature = TextField(verbose_name="Assinatura", null=True, blank=True)
    allow_schedule_client_same_time = models.BooleanField(
        verbose_name="Permitir agendar com o colaborador no mesmo horário",
        default=False,
    )
    allow_schedule_customer_same_time = models.BooleanField(
        verbose_name="Permitir agendar o cliente no mesmo horário", default=False
    )

    crm_lead_distribution_type = models.CharField(
        max_length=20,
        choices=CRM_LEAD_DISTRIBUTION_TYPE_CHOICES,
        default=RANDOM,
        verbose_name="Tipo de distribuição de leads",
    )
    crm_customer_distribution_type = models.CharField(
        max_length=20,
        choices=CRM_CUSTOMER_DISTIBUTION_TYPE_CHOICES,
        default=RANDOM,
        verbose_name="Tipo de distribuição de clientes",
    )
    crm_leads_maximum_quantity = models.IntegerField(
        verbose_name="Quantidade máxima de leads por colaborador", default=5
    )
    crm_opportunity_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo de expiração de lead em oportunidade", default=76
    )
    crm_schedule_made_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo de expiração de lead em agendamento realizado",
        default=120,
    )
    crm_budget_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo de expiração de lead em orçamento", default=90
    )
    crm_warn_lead_expiration_time = models.IntegerField(
        verbose_name="Tempo para aviso de expiração de lead", default=4
    )

    crm_time_to_lead_inativation_without_budget = models.IntegerField(
        verbose_name="Tempo para inativação de oportunidade sem orçamento em dias",
        default=90,
    )
    crm_status_change_time_hot = models.IntegerField(
        verbose_name="Tempo para troca de status: Quente", default=12
    )
    crm_status_change_time_warm = models.IntegerField(
        verbose_name="Tempo para troca de status: Morno", default=48
    )
    crm_status_change_time_cold = models.IntegerField(
        verbose_name="Tempo para troca de status: Frio", default=72
    )
    crm_maximum_tags_display = models.IntegerField(
        verbose_name="Exibição máxima de tags", default=5
    )
    courtesy_royalty_percentage = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Percentual do faturamento de cortesia sem cobrança de royalties",
        default=0,
    )
    minimum_installment_percentage = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Percentual mínimo de parcela para liberar parcela de valor pendente",
        default=0,
    )
    crm_allow_facebook_api = models.BooleanField(
        verbose_name="Permitir api do facebook", default=False
    )
    hide_schedule_finished = models.BooleanField(
        verbose_name="Ocultar agendamentos com status finalizado?", default=False
    )
    hide_schedule_canceled = models.BooleanField(
        verbose_name="Ocultar agendamentos com status cancelado?", default=False
    )
    hide_schedule_missed = models.BooleanField(
        verbose_name="Ocultar agendamentos com status faltou?", default=False
    )
    hide_schedule_missed_confirmed = models.BooleanField(
        verbose_name="Ocultar agendamentos com status faltou confirmado?", default=False
    )
    crm_allow_heheritage_of_history_on_transfer = models.BooleanField(
        verbose_name="Permitir a herança do historico do Lead na transferencia de associados?",
        default=False,
    )

    crm_lead_absent_time_limit = models.IntegerField(
        verbose_name="Tempo (em dias) para lead se tornar ausente", default=15
    )
    crm_absent_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo (em dias) de expiração de lead em ausente",
        default=15,
    )
    crm_scheduled_absent_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo (em dias) de expiração de lead em agendado (ausente)",
        default=15,
    )

    crm_renovation_type = models.CharField(
        max_length=20,
        choices=CRM_RENOVATION_TYPE_CHOICES,
        default=SERVICE,
        verbose_name="Tipo de renovação dos leads",
    )
    crm_renovation_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo (em dias) de expiração de lead em renovação",
        default=280,
    )
    crm_renovation_percentage = models.DecimalField(
        verbose_name="Percentual para renovação",
        max_digits=6,
        decimal_places=2,
        default=80.0,
    )
    crm_retention_warn_lead_expiration_time = models.IntegerField(
        verbose_name="Tempo (em horas) para aviso de expiração de lead no CRM de retenção",
        default=4,
    )
    crm_recovery_lead_expiration_time_limit = models.IntegerField(
        verbose_name="Limite de tempo (em dias) de expiração de lead em resgate",
        default=15,
    )
    crm_recovery_lead_start_time = models.IntegerField(
        verbose_name="Limite de tempo (em dias) para iniciar resgate de lead",
        default=280,
    )
    crm_recovery_lead_end_time = models.IntegerField(
        verbose_name="Limite de tempo (em dias) para encerrar resgate de lead",
        default=720,
    )
    crm_must_move_to_opportunity = models.BooleanField(
        verbose_name="Obrigatório mover para oportunidade?", default=False
    )
    display_service_abbreviation_in_scheduling = models.BooleanField(
        verbose_name="Exibir abreviação do serviço no agendamento?", default=False
    )
    customer_new_time_limit = models.IntegerField(
        verbose_name="Tempo (em dias) para cliente ser considerado novo", default=30
    )
    show_countdown = models.BooleanField(
        verbose_name="Exibir contagem regressiva para expiração do lead?", default=True
    )
    show_tasks_on_login = models.BooleanField(
        verbose_name="Exibir modal de tarefas no login do usuário?", default=False
    )
    require_professional_on_schedule_room_view = models.BooleanField(
        verbose_name="Origatório atribuir profissional ao criar agendamento na visualização por sala?",
        default=True,
    )
    schedule_week_start_day = models.CharField(
        max_length=20,
        choices=START_WEEK_CHOICES,
        default=ON_SUNDAY,
        verbose_name="Inicio da semana na visualização semanal da agenda",
    )

    schedule_max_aditional_duration = models.IntegerField(
        verbose_name="Tempo (em minutos) para aumentar a duração de um agendamento",
        default=0,
    )
    schedule_min_aditional_duration = models.IntegerField(
        verbose_name="Tempo (em minutos) para diminuir a duração de um agendamento",
        default=0,
    )

    allow_retroactive_scheduling = models.BooleanField(
        verbose_name="Permitir agendamento retroativo", default=True
    )
    require_signature_on_schedule = models.BooleanField(
        verbose_name="Obrigatório assinatura no agendamento", default=True
    )
    allow_default_forms_on_sku_type = models.BooleanField(
        verbose_name="Permitir uso de formulários padrões nos tipos de serviço",
        default=False,
    )
    allow_scheduling_without_signed_contract = models.BooleanField(
        verbose_name="Permitir agendamento sem contrato assinado", default=True
    )
    allow_scheduling_without_signed_term = models.BooleanField(
        verbose_name="Permitir agendamento sem o termo adicional assinado", default=True
    )

    allow_schedule_more_than_one_consulting = models.BooleanField(
        verbose_name="Permitir agendar mais de uma avaliação por cliente", default=True
    )

    class Meta:
        managed = False
        db_table = "corporate_group_unity_parameterization"


class CrmCampaign(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=5000, blank=True, null=True)
    abbreviated_name = models.CharField(max_length=10)
    initial_date = models.DateField()
    final_date = models.DateField()
    regulation = models.CharField(max_length=50000)
    send_franchisor = models.BooleanField()
    send_franchisee = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_campaign"


class CrmCampaignAttachment(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=500)
    campaign = models.ForeignKey(CrmCampaign, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "crm_campaign_attachment"


class CrmCampaignUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(CrmCampaign, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "crm_campaign_unity"


class CrmCustomerSource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=30)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_customer_source"


class CrmCustomerSourceCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=30)
    campaign = models.CharField(max_length=20)
    customer_who_recommended = models.CharField(max_length=20)
    contact_who_recommended = models.CharField(max_length=20)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_customer_source_category"


class CrmMedia(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=5000)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    media_group = models.ForeignKey(
        "CrmMediaGroup", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_media"


class CrmMediaGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_media_group"


class CrmMediaUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    media = models.ForeignKey(CrmMedia, on_delete=CASCADE)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, on_delete=CASCADE)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_media_unity"


class CrmTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity_id = models.BigIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_tag"


class Dashboard(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=30)
    access_user = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.OneToOneField(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "dashboard"


class DocumentType(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    natural_person = models.BooleanField()
    legal_person = models.BooleanField()
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    location_country = models.ForeignKey("LocationCountry", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "document_type"


class FinanceAccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=20)
    routing_number = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_bank = models.ForeignKey(
        "FinanceBank", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_account"
        unique_together = (
            (
                "corporate_group_unity",
                "type",
                "finance_bank",
                "routing_number",
                "account_number",
            ),
        )


class FinanceAccountBalance(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    variation = models.CharField(max_length=8)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_account = models.ForeignKey(FinanceAccount, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_account_balance"
        unique_together = (("finance_account", "variation"),)


class FinanceBank(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    location_country = models.ForeignKey("LocationCountry", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "finance_bank"


class FinanceCardLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=30)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    logo_image = models.OneToOneField(
        CoreFile, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_card_label"


class FinanceCardProcessor(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_card_processor"


class FinanceCardProcessorLabel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    remainder_division_installment = models.CharField(max_length=30)
    processing_fee_percent_debit = models.DecimalField(max_digits=10, decimal_places=4)
    processing_fee_min_value = models.DecimalField(max_digits=18, decimal_places=2)
    subtract_fee_from_installment = models.BooleanField()
    days_first_due_date = models.IntegerField()
    days_between_payment_and_credit = models.IntegerField()
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_card_label = models.ForeignKey(
        FinanceCardLabel, models.DO_NOTHING, blank=True, null=True
    )
    finance_card_processor = models.ForeignKey(FinanceCardProcessor, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_card_processor_label"
        unique_together = (("finance_card_processor", "finance_card_label"),)


class FinanceCardProcessorLabelInstallment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    number_of_installments = models.IntegerField()
    processing_fee_percent = models.DecimalField(max_digits=10, decimal_places=4)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_card_processor_label = models.ForeignKey(
        FinanceCardProcessorLabel, models.DO_NOTHING
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_card_processor_label_installment"
        unique_together = (("finance_card_processor_label", "number_of_installments"),)


class FinanceCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=50, blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    category_parent = models.ForeignKey(
        "self", models.DO_NOTHING, blank=True, null=True
    )
    is_child = models.BooleanField()
    is_parent = models.BooleanField()
    nature = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = "finance_category"


class FinancePaymentInstallment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    payment_amount = models.DecimalField(max_digits=18, decimal_places=2)
    is_paid = models.BooleanField()
    expiration_date = models.DateField()
    payment_date = models.DateField()
    additional_information = models.CharField(max_length=200, blank=True, null=True)
    authorization_code = models.CharField(max_length=50, blank=True, null=True)
    no_bank_draft = models.IntegerField(blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_payment_option = models.ForeignKey(
        "FinancePaymentOption", models.DO_NOTHING
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_order = models.ForeignKey(
        "SalesOrder", models.DO_NOTHING, blank=True, null=True
    )
    transaction = models.ForeignKey(
        "FinanceTransactions", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_payment_installment"


class FinancePaymentOption(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    min_number_of_installments = models.IntegerField()
    max_number_of_installments = models.IntegerField()
    allowed_for_sale = models.BooleanField()
    allowed_for_purchase = models.BooleanField()
    is_recurrent = models.BooleanField()
    is_change_allowed = models.BooleanField()
    acquirer = models.ForeignKey(Acquirer, models.DO_NOTHING, blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_account = models.ForeignKey(
        FinanceAccount, models.DO_NOTHING, blank=True, null=True
    )
    finance_card_processor = models.ForeignKey(
        FinanceCardProcessor, models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    auto_payable = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "finance_payment_option"


class FinanceTransactions(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    is_paid = models.BooleanField()
    expiration_date = models.DateField()
    payment_date = models.DateField(blank=True, null=True)
    additional_information = models.CharField(max_length=200, blank=True, null=True)
    authorization_code = models.CharField(max_length=50, blank=True, null=True)
    transaction_type = models.CharField(max_length=45)
    check_number = models.CharField(max_length=150, blank=True, null=True)
    pix_number = models.CharField(max_length=150, blank=True, null=True)
    nsu = models.CharField(max_length=150, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=18, decimal_places=2)
    pix_code = models.CharField(max_length=32, blank=True, null=True)
    acquirer = models.ForeignKey(Acquirer, models.DO_NOTHING, blank=True, null=True)
    acquirer_flag = models.ForeignKey(
        AcquirerFlag, models.DO_NOTHING, blank=True, null=True
    )
    cash_register = models.ForeignKey(
        CashRegister, models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey("Partner", models.DO_NOTHING, blank=True, null=True)
    destination_account = models.ForeignKey(
        FinanceAccount, models.DO_NOTHING, blank=True, null=True
    )
    finance_account = models.ForeignKey(
        FinanceAccount, models.DO_NOTHING, blank=True, null=True
    )
    finance_payment_option = models.ForeignKey(FinancePaymentOption, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    origin_account = models.ForeignKey(
        FinanceAccount, models.DO_NOTHING, blank=True, null=True
    )
    sales_order = models.ForeignKey(
        "SalesOrder", models.DO_NOTHING, blank=True, null=True
    )
    supplier = models.ForeignKey("Partner", models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(
        FinanceCategory, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "finance_transactions"


class Form(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=255)
    comments = models.TextField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    last_form_version = models.OneToOneField(
        "FormVersion", models.DO_NOTHING, blank=True, null=True
    )
    last_published_form_version = models.OneToOneField(
        "FormVersion", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "form"


class FormQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    version = models.IntegerField()
    sequence = models.IntegerField()
    possible_responses = models.JSONField()
    title = models.CharField(max_length=1000)
    type = models.CharField(max_length=30)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form = models.ForeignKey(Form, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "form_question"


class FormQuestionResponse(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    response = models.JSONField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form_question = models.ForeignKey(
        FormQuestion, models.DO_NOTHING, blank=True, null=True
    )
    form_response = models.ForeignKey("FormResponse", models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "form_question_response"


class FormResponse(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    response = models.JSONField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form = models.ForeignKey(Form, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    schedule_sku_resource = models.ForeignKey(
        "ScheduleSkuResource", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "form_response"


class FormSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    form_type = models.CharField(max_length=10)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form = models.ForeignKey(Form, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "form_sku"


class FormVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    is_published = models.BooleanField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form = models.ForeignKey(Form, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "form_version"


class HumanResourceAbsenceJustification(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    description = models.CharField(max_length=50)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "human_resource_absence_justification"


class HumanResourceJustifiedAbsence(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    comments = models.CharField(max_length=300)
    certificate = models.CharField(max_length=100, blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    human_resource_absence_justification = models.ForeignKey(
        HumanResourceAbsenceJustification, models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey("Partner", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "human_resource_justified_absence"


class HumanResourcePayrollPeriod(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    period = models.CharField(max_length=6)
    is_blocked = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "human_resource_payroll_period"


class HumanResourcePayrollPeriodPartner(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    period = models.CharField(max_length=6)
    is_blocked = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey("Partner", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "human_resource_payroll_period_partner"


class HumanResourceTimeKeepingEmployee(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    datetime = models.DateTimeField()
    event_type = models.CharField(max_length=5)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey("Partner", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "human_resource_time_keeping_employee"


class HumanResourceWorkingHour(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    weekday = models.CharField(max_length=1)
    entry_time = models.TimeField(blank=True, null=True)
    exit_time = models.TimeField(blank=True, null=True)
    break_entry_time = models.TimeField(blank=True, null=True)
    break_time = models.TimeField(blank=True, null=True)
    closed = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey("Partner", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "human_resource_working_hour"


class LocationCity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    federal_code = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    location_state = models.ForeignKey("LocationState", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "location_city"


class LocationCountry(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    abbreviated_name = models.CharField(max_length=2)
    idd_code = models.IntegerField()
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    language = models.ForeignKey("LocationLanguage", models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "location_country"


class LocationLanguage(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    abbreviated_name = models.CharField(max_length=10)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "location_language"


class LocationState(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    abbreviated_name = models.CharField(max_length=2)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    location_country = models.ForeignKey(LocationCountry, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "location_state"


class MediaMedias(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=40)
    description = models.TextField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "media_medias"


class Partner(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=30)
    login_name = models.CharField(max_length=100)
    password = models.CharField(max_length=50, blank=True, null=True)
    person_type = models.CharField(max_length=50)
    federal_tax_number = models.CharField(max_length=50, blank=True, null=True)
    state_tax_number = models.CharField(max_length=50)
    city_tax_number = models.CharField(max_length=50)
    federal_register_number = models.CharField(max_length=50)
    birth_date = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=30)
    mobile = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    business_phone = models.CharField(max_length=20)
    have_federal_tax_number = models.BooleanField()
    whatsapp_number = models.CharField(max_length=20)
    trade_name = models.CharField(max_length=200)
    marital_status = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    address_number = models.CharField(max_length=20)
    address_neighborhood = models.CharField(max_length=100)
    address_complement = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    email = models.CharField(max_length=200)
    schedule_notification_mail = models.BooleanField(blank=True, null=True)
    schedule_notification_sms = models.BooleanField(blank=True, null=True)
    schedule_notification_whatsapp = models.BooleanField(blank=True, null=True)
    media_source_id = models.IntegerField(blank=True, null=True)
    customer_responsible_name = models.CharField(max_length=100)
    customer_responsible_legal_id = models.CharField(
        max_length=50, blank=True, null=True
    )
    employee_position = models.CharField(max_length=50)
    employee_legal_id = models.CharField(max_length=50)
    employee_legal_id_a1 = models.CharField(max_length=50)
    employee_legal_id_a2 = models.CharField(max_length=20)
    employee_salary = models.DecimalField(max_digits=18, decimal_places=2)
    employee_hire_date = models.DateField(blank=True, null=True)
    employee_dismissal_date = models.DateField(blank=True, null=True)
    employee_benefits = models.CharField(max_length=200)
    is_customer = models.BooleanField()
    is_supplier = models.BooleanField()
    is_employee = models.BooleanField()
    is_user = models.BooleanField()
    is_corporate_unity = models.BooleanField()
    is_unity_owner = models.BooleanField()
    is_professional = models.BooleanField()
    investor_only = models.BooleanField()
    coordinate_latitude = models.DecimalField(
        max_digits=8, decimal_places=6, blank=True, null=True
    )
    coordinate_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    coordinate_update_date = models.DateField(blank=True, null=True)
    work_card = models.CharField(max_length=7, blank=True, null=True)
    serial_number = models.CharField(max_length=4, blank=True, null=True)
    pis = models.CharField(max_length=11, blank=True, null=True)
    transportation_voucher = models.CharField(max_length=10, blank=True, null=True)
    meal_voucher = models.CharField(max_length=10, blank=True, null=True)
    other_voucher = models.CharField(max_length=10, blank=True, null=True)
    bank = models.CharField(max_length=50, blank=True, null=True)
    agency = models.CharField(max_length=6, blank=True, null=True)
    checking_account = models.CharField(max_length=21, blank=True, null=True)
    foreign_tax_number = models.CharField(max_length=11)
    identity_card_number = models.CharField(max_length=50)
    issuing_agency = models.CharField(max_length=3)
    receive_email = models.BooleanField()
    receive_sms = models.BooleanField()
    receive_whats = models.BooleanField()
    description = models.CharField(max_length=1024, blank=True, null=True)
    classification = models.CharField(max_length=10, blank=True, null=True)
    customer_code = models.CharField(max_length=10, blank=True, null=True)
    cell_phone_operator = models.CharField(max_length=15, blank=True, null=True)
    point_registry = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    customer_corporate_unity = models.ForeignKey(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )
    customer_last_attendant_unity = models.ForeignKey(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    location_city = models.ForeignKey(
        LocationCity, models.DO_NOTHING, blank=True, null=True
    )
    location_country = models.ForeignKey(
        LocationCountry, models.DO_NOTHING, blank=True, null=True
    )
    location_state = models.ForeignKey(
        LocationState, models.DO_NOTHING, blank=True, null=True
    )
    main_unit = models.ForeignKey(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )
    media = models.ForeignKey(CrmMedia, models.DO_NOTHING, blank=True, null=True)
    referral_customer = models.ForeignKey(
        "self", models.DO_NOTHING, blank=True, null=True
    )
    # supplier_corporate_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True)
    type_media = models.ForeignKey(
        CrmMediaGroup, models.DO_NOTHING, blank=True, null=True
    )
    federal_register_document_type = models.ForeignKey(
        DocumentType, models.DO_NOTHING, blank=True, null=True
    )
    federal_tax_document_type = models.ForeignKey(
        DocumentType, models.DO_NOTHING, blank=True, null=True
    )
    foreign_tax_document_type = models.ForeignKey(
        DocumentType, models.DO_NOTHING, blank=True, null=True
    )
    occupation = models.CharField(max_length=100, blank=True, null=True)
    type_contract = models.CharField(max_length=100, blank=True, null=True)
    # is_sales_representative = models.BooleanField(default=False)
    whatsapp_integration_code = models.CharField(max_length=500, blank=True, null=True)
    social_name = models.CharField(max_length=100)

    LEAD_CUSTOMER = "lead"
    REGISTERED_CUSTOMER = "registered"
    CONVERTED_CUSTOMER = "converted"

    class Meta:
        managed = False
        db_table = "partner"


class PartnerAnnotation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    alert = models.BooleanField()
    alert_published_in = models.CharField(max_length=30)
    annotation_type = models.CharField(max_length=100)
    motive = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    detailed_description = models.CharField(max_length=200)
    initial_date = models.DateTimeField(blank=True, null=True)
    final_date = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    created_by_unity = models.ForeignKey(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_annotation"


class PartnerAnnotationShowAlert(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30)
    partner_annotation = models.ForeignKey(PartnerAnnotation, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_annotation_show_alert"


class PartnerAnnotationUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    partner_annotation = models.ForeignKey(PartnerAnnotation, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_annotation_unity"


class PartnerBankAccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    routing_number = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    finance_bank = models.ForeignKey(FinanceBank, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_bank_account"


class PartnerCrmTag(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING, blank=True, null=True)
    tag = models.ForeignKey(CrmTag, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_crm_tag"


class PartnerCustomerAccount(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    generated_value = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    reason = models.CharField(max_length=255, blank=True, null=True)
    # is_credit = models.BooleanField()
    # is_debit = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey(Partner, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_order = models.ForeignKey("SalesOrder", models.DO_NOTHING)
    transfer_type = models.CharField(max_length=45)
    exit = models.BooleanField()

    class Meta:
        managed = False
        db_table = "partner_customer_account"


class PartnerCustomerAlert(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    publication = models.CharField(max_length=30)
    alert = models.CharField(max_length=200)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_customer_alert"


class PartnerCustomerAlertUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    partner_customer_alert = models.ForeignKey(PartnerCustomerAlert, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_customer_alert_unity"


class PartnerFormResponse(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    form_response = models.ForeignKey(FormResponse, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_form_response"


class PartnerNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    target = models.CharField(max_length=50)
    media = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=50)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_notification"


class PartnerPicture(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    sequence = models.IntegerField()
    core_file = models.OneToOneField(CoreFile, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_picture"


class PartnerSocialMedia(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    social_media = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_social_media"
        unique_together = (("partner", "social_media"),)


class PartnerUnityCustomer(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    customer_id = models.BigIntegerField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_unity_customer"


class PartnerUnitySupplier(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_unity_supplier"


class PartnerUnityUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    access_profile = models.ForeignKey(AccessProfile, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING)
    is_allowed_receive_opportunity = models.BooleanField(default=False)
    is_allowed_receive_customer = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "partner_unity_user"
        unique_together = (
            ("partner", "access_profile", "corporate_group_unity"),
            ("partner", "corporate_group_unity"),
        )


class PriceList(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    send_franchisor = models.BooleanField()
    send_franchisee = models.BooleanField()
    current = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "price_list"


class PriceListSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    price = models.DecimalField(max_digits=18, decimal_places=2)
    price_list = models.ForeignKey(PriceList, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    discount_price = models.DecimalField(max_digits=18, decimal_places=2)
    maximum_discount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = "price_list_sku"


class PriceListUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    id = models.BigAutoField(primary_key=True)
    current = models.BooleanField()
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    price_list = models.ForeignKey(PriceList, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "price_list_unity"


class PricePromotion(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    discount_type = models.CharField(max_length=30)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    min_order_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    max_order_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    min_item_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    max_item_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    weekdays = models.CharField(max_length=30)
    daily_start_time = models.TimeField()
    daily_end_time = models.TimeField()
    uses_cashback_in_promotions = models.BooleanField()
    uses_cashback_in_products = models.BooleanField()
    uses_cashback_in_single_sessions = models.BooleanField()
    min_days_for_cashback = models.IntegerField(blank=True, null=True)
    max_days_for_cashback = models.IntegerField(blank=True, null=True)
    min_order_discount_percent = models.DecimalField(max_digits=5, decimal_places=3)
    max_order_discount_percent = models.DecimalField(max_digits=5, decimal_places=3)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "price_promotion"


class Resource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50)
    is_consultant = models.BooleanField()
    type = models.CharField(max_length=20)
    specific_control = models.CharField(max_length=50)
    has_schedule_control = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    equipment_sku = models.ForeignKey("Sku", models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner = models.ForeignKey(Partner, models.DO_NOTHING, blank=True, null=True)
    is_integration_resource = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "resource"


class ResourceAvailableTime(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    weekday = models.CharField(max_length=1)
    entry_time = models.TimeField(blank=True, null=True)
    exit_time = models.TimeField(blank=True, null=True)
    break_entry_time = models.TimeField(blank=True, null=True)
    break_time = models.TimeField(blank=True, null=True)
    closed = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource = models.ForeignKey(Resource, models.DO_NOTHING)
    is_exception = models.BooleanField(default=False, verbose_name="É exceção?")
    exception_reason = models.CharField(
        max_length=200, verbose_name="Motivo da exceção", null=True
    )
    date = models.DateField(verbose_name="data inícial da taxação", null=True)

    class Meta:
        managed = False
        db_table = "resource_available_time"


class ResourceCorporateGroupUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource = models.ForeignKey(Resource, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "resource_corporate_group_unity"
        unique_together = (("resource", "corporate_group_unity"),)


class ResourcePerformsSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource = models.ForeignKey(Resource, models.DO_NOTHING)
    sku_service = models.ForeignKey("Sku", models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(
        CorporateGroupUnity, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "resource_performs_sku"
        unique_together = (("sku_service", "resource"),)


class ResourceProfessionalPerformsSkuService(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource_professional = models.ForeignKey(Resource, models.DO_NOTHING)
    sku_service = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "resource_professional_performs_sku_service"
        unique_together = (("sku_service", "resource_professional"),)


class SalesChannel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=50)
    control_type = models.CharField(max_length=30)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "sales_channel"


class SalesDiscount(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    type = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    display_in_separate_services = models.BooleanField()
    maximum_discount_separate_services = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    display_in_packages = models.BooleanField()
    maximum_discount_packages = models.DecimalField(max_digits=18, decimal_places=2)
    display_in_products = models.BooleanField()
    maximum_discount_products = models.DecimalField(max_digits=18, decimal_places=2)
    unity_limit = models.BooleanField()
    unity_quantity = models.IntegerField(blank=True, null=True)
    document_number_limit = models.BooleanField()
    document_number_quantity = models.IntegerField(blank=True, null=True)
    customer_limit = models.BooleanField()
    customer_quantity = models.IntegerField(blank=True, null=True)
    restrict_services = models.BooleanField()
    payment_forms_limit = models.BooleanField()
    allow_customer_without_ftn = models.BooleanField()
    allow_birthday_person = models.BooleanField()
    birthday_break_days = models.IntegerField(blank=True, null=True)
    allow_another_discount_reason = models.BooleanField()
    discount_reflects_commission = models.BooleanField(blank=True, null=True)
    affects_comission = models.BooleanField()
    display_discount_reason_on = models.CharField(max_length=200)
    campaign_linked = models.BooleanField()
    regulation = models.CharField(max_length=10000)
    send_franchisor = models.BooleanField()
    send_franchisee = models.BooleanField()
    initial_date = models.DateField()
    final_date = models.DateField()
    validity_days = models.IntegerField()
    total_value = models.DecimalField(max_digits=18, decimal_places=2)
    generate_cashback = models.BooleanField()
    enable_buy_and_win = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    generate_contract = models.BooleanField()

    class Meta:
        managed = False
        db_table = "sales_discount"


class SalesDiscountBuyWinSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    quantity = models.IntegerField()
    discount_percent = models.DecimalField(max_digits=18, decimal_places=2)
    discount_value = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_buy_win_sku"


class SalesDiscountCampaign(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    abbreviated_name = models.CharField(max_length=10, blank=True, null=True)
    initial_date = models.DateField(blank=True, null=True)
    final_date = models.DateField(blank=True, null=True)
    regulation = models.CharField(max_length=50000, blank=True, null=True)
    send_franchisor = models.BooleanField(blank=True, null=True)
    send_franchisee = models.BooleanField(blank=True, null=True)
    campaign = models.ForeignKey(CrmCampaign, models.DO_NOTHING, blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_campaign"


class SalesDiscountCashback(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    release_days = models.IntegerField()
    expiration_days = models.IntegerField()
    generated_cashback_percentage = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_cashback"


class SalesDiscountPackageSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    quantity = models.IntegerField()
    discount_percent = models.DecimalField(max_digits=18, decimal_places=2)
    discount_value = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_package_sku"


class SalesDiscountPaymentOption(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    payment_option = models.ForeignKey(FinancePaymentOption, models.DO_NOTHING)
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_payment_option"


class SalesDiscountRestrictedService(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_restricted_service"


class SalesDiscountSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=18, decimal_places=2)
    discount_value = models.DecimalField(max_digits=18, decimal_places=2)
    editable = models.BooleanField()
    removable = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)
    sales_order = models.ForeignKey("SalesOrder", models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)
    sale_order_sku = models.ForeignKey("SalesOrderSku", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_sku"


class SalesDiscountUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_discount = models.ForeignKey(SalesDiscount, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_discount_unity"


class SalesOrder(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    customer_name = models.CharField(max_length=100)
    total_list_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_net_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_effective_price = models.DecimalField(max_digits=18, decimal_places=2)
    customer_phone = models.CharField(max_length=20)
    order_type = models.CharField(max_length=20)
    order_source = models.CharField(max_length=20)
    quote_due_date = models.DateField(blank=True, null=True)
    order_status = models.CharField(max_length=20)
    order_status_service = models.CharField(max_length=20)
    comment = models.CharField(max_length=1000)
    sale_date = models.DateTimeField()
    voucher_number = models.IntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_discount_price = models.DecimalField(max_digits=18, decimal_places=2)
    has_product = models.BooleanField()
    has_package = models.BooleanField()
    has_service = models.BooleanField()
    has_courtesy = models.BooleanField()
    exempt_fine = models.BooleanField()
    fine_percentage = models.IntegerField(blank=True, null=True)
    fine_value = models.DecimalField(max_digits=18, decimal_places=6)
    reason_rescission = models.CharField(max_length=200, blank=True, null=True)
    total_value_used = models.DecimalField(max_digits=18, decimal_places=6)
    cancel_value = models.DecimalField(max_digits=18, decimal_places=6)
    total_value_returned = models.DecimalField(max_digits=18, decimal_places=6)
    rescission_on = models.DateTimeField(blank=True, null=True)
    transfer_reason = models.CharField(max_length=200, blank=True, null=True)
    discount_reason = models.CharField(max_length=200, blank=True, null=True)
    finished = models.BooleanField()
    attendance_linked = models.ForeignKey(
        "Schedule", models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    customer_partner = models.ForeignKey(
        Partner, models.DO_NOTHING, blank=True, null=True
    )
    indicator_partner = models.ForeignKey(
        Partner, models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner_user = models.ForeignKey(Partner, models.DO_NOTHING)
    rescission_user = models.ForeignKey(
        Partner, models.DO_NOTHING, blank=True, null=True
    )
    sales_media = models.ForeignKey(CrmMedia, models.DO_NOTHING, blank=True, null=True)
    consulting_linked = models.ForeignKey(
        "Schedule", models.DO_NOTHING, blank=True, null=True
    )
    sales_media_type = models.ForeignKey(
        CrmMediaGroup, models.DO_NOTHING, blank=True, null=True
    )
    # indicator_partner_type = models.CharField(max_length=20, blank=True, null=True)
    credit_used = models.DecimalField(max_digits=18, decimal_places=6)
    indicator_customer = models.ForeignKey(
        Partner, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "sales_order"


class SalesOrderSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    quantity_sold = models.IntegerField()
    quantity_used = models.IntegerField()
    quantity_cancelled = models.IntegerField(default=0)
    quantity_available = models.IntegerField(default=0)
    quantity_canceled_other_systems = models.IntegerField(default=0)
    quantity_used_other_systems = models.IntegerField(default=0)
    finished = models.BooleanField()
    price = models.DecimalField(max_digits=18, decimal_places=2)
    unit_list_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_list_price = models.DecimalField(max_digits=18, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=5)
    discount_value = models.DecimalField(max_digits=18, decimal_places=2)
    total_net_price = models.DecimalField(max_digits=18, decimal_places=2)
    total_effective_price = models.DecimalField(max_digits=18, decimal_places=2)
    expiration_date = models.DateField()
    sku_number = models.CharField(max_length=50)
    can_add_discount = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    package = models.ForeignKey(SalesDiscount, models.DO_NOTHING, blank=True, null=True)
    sales_order = models.ForeignKey(SalesOrder, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING, blank=True, null=True)
    quantity_scheduled = models.IntegerField()
    quantity_exchanged_for_credit = models.IntegerField(default=0)
    updates_count = models.IntegerField()
    is_courtesy = models.BooleanField(default=False)
    quantity_desconted = models.IntegerField(default=0)
    has_cancelled = models.BooleanField(default=False)
    quantity_desconted_bkp = models.IntegerField(default=0)
    quantity_script_execution = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "sales_order_sku"


class SalesOrderSkuSchedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_order_sku = models.ForeignKey(SalesOrderSku, models.DO_NOTHING)
    schedule = models.ForeignKey("Schedule", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_order_sku_schedule"


class Schedule(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.TimeField(blank=True, null=True)
    timezone = models.CharField(max_length=50)
    type = models.CharField(max_length=30)
    comments = models.CharField(max_length=5000)
    attendance_start_time = models.DateTimeField(blank=True, null=True)
    attendance_end_time = models.DateTimeField(blank=True, null=True)
    attendance_time = models.BigIntegerField(blank=True, null=True)
    attendance_last_start_time = models.DateTimeField(blank=True, null=True)
    attendance_custumer_mood = models.CharField(max_length=50, blank=True, null=True)
    attendance_custumer_comments = models.CharField(
        max_length=300, blank=True, null=True
    )
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    partner_customer = models.ForeignKey(
        Partner, models.DO_NOTHING, blank=True, null=True
    )
    partner_user = models.ForeignKey(Partner, models.DO_NOTHING, blank=True, null=True)
    sales_order = models.ForeignKey(
        SalesOrder, models.DO_NOTHING, blank=True, null=True
    )
    session_number = models.IntegerField(blank=True, null=True)
    status = models.ManyToManyField(
        "ScheduleStatus",
        through="ScheduleStatusDetail",
        verbose_name="Status",
        help_text="Status do agendamento",
    )

    class Meta:
        managed = False
        db_table = "schedule"


class ScheduleAttendanceBehavior(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    attendance_behavior = models.ForeignKey(AttendanceBehavior, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_attendance_behavior"


class ScheduleAttendanceSensitivity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    attendance_sensitivity = models.ForeignKey(AttendanceSensitivity, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_attendance_sensitivity"


class ScheduleLock(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    description = models.TextField()
    reason = models.TextField()
    block_type = models.CharField(max_length=23)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_lock"


class ScheduleLockResource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    resource = models.ForeignKey(Resource, models.DO_NOTHING)
    schedule_lock = models.ForeignKey(ScheduleLock, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_lock_resource"


class ScheduleResource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    estimated_quantity = models.DecimalField(max_digits=18, decimal_places=6)
    um = models.CharField(max_length=3)
    estimated_time = models.DurationField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource = models.ForeignKey(Resource, models.DO_NOTHING)
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_resource"


class ScheduleSku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    estimated_time = models.DurationField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING)

    # sales_order_sku = models.ForeignKey("SalesOrderSku", models.DO_NOTHING, null=True)

    class Meta:
        managed = False
        db_table = "schedule_sku"


class ScheduleSkuResource(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    resource = models.ForeignKey(Resource, models.DO_NOTHING)
    sales_order_sku = models.ForeignKey(
        SalesOrderSku, models.DO_NOTHING, blank=True, null=True
    )
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)
    sku = models.ForeignKey("Sku", models.DO_NOTHING, blank=True, null=True)
    begin_time = models.DateTimeField()
    duration = models.TimeField(blank=True, null=True)
    end_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "schedule_sku_resource"


class ScheduleStatus(models.Model):
    SCHEDULED = "scheduled"
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    PRESENT = "present"
    FINISHED = "finished"
    NEW_CUSTOMER = "new_customer"
    MISSED = "missed"
    MISSED_CONFIRMED = "missed_confirmed"
    CANCELED = "canceled"
    IN_ANALYSIS = "in_analysis"
    PENDING_AMOUNTS = "pending_amounts"
    BIRTHDAY = "birthday"
    CALL_CENTER = "call_center"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    PROGRESS = "progress"
    PAUSED = "paused"
    MISSED_FEDERAL_ID = "missed_federal_id"
    PENDING_INFORMATION = "pending_information"
    DEMONSTRATION = "demonstration"
    REPLACEMENT = "replacement"
    COURTESY = "courtesy"
    PRESALE = "presale"

    STATUS_CHOICES = [
        (SCHEDULED, "Agendado"),
        (RESERVED, "Reservado"),
        (CONFIRMED, "Confirmado"),
        (PRESENT, "Presente"),
        (FINISHED, "Finalizado"),
        (NEW_CUSTOMER, "Cliente Novo"),
        (MISSED, "Faltou"),
        (MISSED_CONFIRMED, "Faltou Confirmado"),
        (CANCELED, "Cancelado"),
        (IN_ANALYSIS, "Em análise"),
        (PENDING_AMOUNTS, "Valores Pendentes"),
        (BIRTHDAY, "Aniversário"),
        (CALL_CENTER, "Central de Atendimento"),
        (WEBSITE, "Website"),
        (MOBILE_APP, "App Mobile"),
        (PROGRESS, "Em Andamento"),
        (PAUSED, "Pausado"),
        (MISSED_FEDERAL_ID, "Falta CPF"),
        (PENDING_INFORMATION, "Pendente de Informações"),
        (DEMONSTRATION, "Demonstração"),
        (REPLACEMENT, "Reposição"),
        (COURTESY, "Cortesia"),
        (PRESALE, "Pré-venda"),
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name="Status",
    )
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=50)
    abbreviated_name = models.CharField(max_length=10)
    icon_color_hex = models.CharField(max_length=7)
    icon_html_code = models.CharField(max_length=5000)
    highlight_color = models.CharField(max_length=5000)
    master_status = models.BooleanField(blank=True, null=True)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "schedule_status"
        unique_together = (("corporate_group", "status"),)


class ScheduleStatusDetail(models.Model):
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    id = models.BigAutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, models.DO_NOTHING)
    schedule_status = models.ForeignKey(ScheduleStatus, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "schedule_status_detail"


class Schedulechangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    type_alteration = models.CharField(max_length=30)
    reason = models.TextField()
    changed_schedule = models.ForeignKey(
        Schedule, models.DO_NOTHING, blank=True, null=True
    )
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    new_schedule = models.ForeignKey(Schedule, models.DO_NOTHING, blank=True, null=True)
    user_id = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    new_schedule_status = models.ForeignKey(
        ScheduleStatus, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "schedulechangelog"


class Sku(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=70)
    default_working_time = models.TimeField(blank=True, null=True)
    sku_number = models.CharField(max_length=50)
    requires_prior_sale = models.BooleanField(blank=True, null=True, default=False)
    is_equipment = models.BooleanField()
    is_product = models.BooleanField()
    # is_separate_session_allowed = models.BooleanField()
    brand = models.CharField(max_length=200, blank=True, null=True)
    product_type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    bar_code = models.CharField(max_length=500, blank=True, null=True)
    gtin_code = models.CharField(max_length=200, blank=True, null=True)
    internal_code = models.CharField(max_length=200, blank=True, null=True)
    ncm = models.CharField(max_length=200, blank=True, null=True)
    minimum_stock = models.FloatField(blank=True, null=True)
    sales_price = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sku_group = models.ForeignKey("SkuGroup", models.DO_NOTHING, blank=True, null=True)
    sku_service_type = models.ForeignKey(
        "SkuServiceType", models.DO_NOTHING, blank=True, null=True
    )
    ums = models.ForeignKey("Um", models.DO_NOTHING, blank=True, null=True)
    sku_equipment_type = models.ForeignKey(
        "SkuEquipmentType", models.DO_NOTHING, blank=True, null=True
    )
    consent_terms = models.TextField(blank=True, null=True)
    assessment_service = models.BooleanField()
    allow_package_sale = models.BooleanField(null=False)
    allow_single_sale = models.BooleanField(null=False)
    need_sign = models.BooleanField(null=False)
    allow_courtesy = models.BooleanField(null=False)
    allow_demonstration = models.BooleanField(null=False)
    # allow_sale = models.BooleanField(null=False)
    allow_schedule_in_call_center = models.BooleanField(null=False)
    quantity_generate_contract = models.IntegerField(default=0)
    quantity_courtesy_per_year = models.IntegerField(default=0)
    allow_replacement = models.BooleanField(null=False)
    allow_pre_sale = models.BooleanField(default=False)
    allow_commissioning = models.BooleanField(default=False)
    return_days_after_execution = models.IntegerField(
        default=0, verbose_name="Quantidade de dias após a execução deve retornar"
    )
    allow_event_discount = models.BooleanField(default=False)
    use_default_sku_type_forms = models.BooleanField(
        verbose_name="Usar formulários padrões do tipo de serviço", default=False
    )
    requires_assessment_single_sale = models.BooleanField(
        verbose_name="Exige avaliação na venda avulsa?",
        default=False,
        null=True,
    )
    requires_assessment_pre_sale = models.BooleanField(
        verbose_name="Exige avaliação na pré-venda?",
        default=False,
        null=True,
    )
    requires_assessment_package_sale = models.BooleanField(
        verbose_name="Exige avaliação na venda de pacote?",
        default=False,
        null=True,
    )

    # pre_attendance_guidelines = models.TextField(
    #     max_length=200,
    #     null=True,
    #     blank=True,
    #     verbose_name="Orientações Pré Atendimento",
    # )
    # pos_attendance_guidelines = models.TextField(
    #     max_length=200,
    #     null=True,
    #     blank=True,
    #     verbose_name="Orientações Pós Atendimento",
    # )

    class Meta:
        managed = False
        db_table = "sku"


class SkuComponent(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    child_quantity = models.DecimalField(max_digits=18, decimal_places=6)
    child_sku_component = models.ForeignKey(Sku, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    parent_sku_component = models.ForeignKey(Sku, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sku_component"


class SkuEquipmentType(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=200)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "sku_equipment_type"


class SkuGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    abbreviated_name = models.CharField(max_length=8)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "sku_group"


class SkuGroupServicesUsesSkuResources(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    equipment_sku = models.ForeignKey(Sku, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    service_group = models.ForeignKey(SkuGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sku_group_services_uses_sku_resources"


class SkuKit(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    child_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    child_sku_kit = models.ForeignKey(Sku, models.DO_NOTHING)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    parent_sku_kit = models.ForeignKey(Sku, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sku_kit"


class SkuSalesChannel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    sales_channel = models.ForeignKey(SalesChannel, models.DO_NOTHING)
    sku = models.ForeignKey(Sku, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sku_sales_channel"


class SkuServiceEquipment(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    index = models.IntegerField()
    time = models.TimeField(blank=True, null=True)
    sku_equipment_type = models.ForeignKey(SkuEquipmentType, models.DO_NOTHING)
    sku = models.ForeignKey(Sku, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sku_service_equipment"


class SkuServiceType(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=30)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "sku_service_type"


class SkuCorporateGroupUnity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    sku = models.ForeignKey(Sku, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'gester"."sku_corporate_group_unity'
        ordering = ["id"]
        unique_together = [["sku", "corporate_group_unity"]]

    def __str__(self):
        return str(self.sku) + " - " + str(self.corporate_group_unity)


class Um(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=50)
    abbreviated_name = models.CharField(max_length=5)
    type = models.CharField(max_length=30)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "um"


class UmConversion(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    multiplier = models.DecimalField(max_digits=22, decimal_places=16)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )
    source_um = models.ForeignKey(Um, models.DO_NOTHING)
    target_um = models.ForeignKey(Um, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "um_conversion"


class UnityCommissioning(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    reference_month = models.DateField()
    unity_achieved_goal_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    unity_achieved_goal_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    unity_achieved_goal_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    professional_achieved_goal_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    professional_achieved_goal_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    professional_achieved_goal_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    commission_without_achieving_goal_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    commission_without_achieving_goal_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    commission_without_achieving_goal_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    treatment_indications_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    treatment_indications_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    treatment_indications_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    treatment_execution_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    treatment_execution_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    treatment_execution_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    creating_partnerships_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    creating_partnerships_fixed_value = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    creating_partnerships_payment_method_percentage = models.DecimalField(
        max_digits=5, decimal_places=2
    )
    total_to_receive = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    corporate_group_unity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    employee = models.ForeignKey(Partner, models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "unity_commissioning"
        unique_together = (("employee", "reference_month"),)


class UnityCommissioningGoals(models.Model):
    id = models.BigAutoField(primary_key=True)
    comissioning = models.ForeignKey(UnityCommissioning, models.DO_NOTHING)
    goal = models.ForeignKey("UnityGoals", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "unity_commissioning_goals"
        unique_together = (("comissioning", "goal"),)


class UnityEmployeeGoals(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    percentage = models.DecimalField(max_digits=8, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    employee = models.ForeignKey(Partner, models.DO_NOTHING)
    goal = models.ForeignKey("UnityGoals", models.DO_NOTHING)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "unity_employee_goals"


class UnityGoals(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    name = models.CharField(max_length=55)
    reference_month = models.DateField()
    description = models.TextField()
    goal_type = models.CharField(max_length=655)
    minimum_amount = models.DecimalField(max_digits=18, decimal_places=2)
    amount_by_unity = models.DecimalField(max_digits=18, decimal_places=2)
    corporate_group = models.ForeignKey(CorporateGroup, models.DO_NOTHING)
    created_by = models.ForeignKey(AccessUser, models.DO_NOTHING, blank=True, null=True)
    last_edit_by = models.ForeignKey(
        AccessUser, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "unity_goals"


class UnityGoalsUnities(models.Model):
    id = models.BigAutoField(primary_key=True)
    goal = models.ForeignKey(UnityGoals, models.DO_NOTHING)
    corporategroupunity = models.ForeignKey(CorporateGroupUnity, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "unity_goals_unities"
        unique_together = (("goal", "corporategroupunity"),)


class LegacyTranslateId(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    legacy_table = models.CharField(max_length=200)
    legacy_id = models.BigIntegerField()
    gester_table = models.CharField(max_length=200)
    gester_id = models.BigIntegerField()
    corporate_group_id = models.BigIntegerField(blank=True, null=True)
    corporate_group_unity_id = models.BigIntegerField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()

    class Meta:
        managed = False
        db_table = "legacy_translate_id"
        unique_together = (
            (
                "legacy_table",
                "legacy_id",
                "gester_table",
                "corporate_group_id",
                "corporate_group_unity_id",
            ),
        )


class LegacyMigrationStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    legacy_unity_id = models.BigIntegerField()
    legacy_table_name = models.CharField(max_length=255)
    last_migration_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "legacy_migration_status"
        unique_together = (("legacy_unity_id", "legacy_table_name"),)


class PipelineItem(models.Model):
    OPPORTUNITY = "opportunity"
    SCHEDULED = "scheduled"
    SCHEDULE_MADE = "schedule_made"
    BUDGET = "budget"
    CONVERTED = "converted"

    PIPELINE_ITEM_CHOICES = [
        (OPPORTUNITY, "Oportunidade"),
        (SCHEDULED, "Agendado"),
        (SCHEDULE_MADE, "Agendamento realizado"),
        (BUDGET, "Orçamento"),
        (CONVERTED, "Convertido"),
    ]
    type = models.CharField(
        verbose_name="ordenação",
        help_text="inicia do 0 e ordena do menor para o maior",
        default=OPPORTUNITY,
        max_length=255,
    )
    name = models.CharField(verbose_name="nome", max_length=255)
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        ordering = ["type"]
        db_table = "crm_pipeline_item"


class Opportunity(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)
    customer = models.ForeignKey(
        Partner, verbose_name="Cliente", on_delete=CASCADE, related_name="opportunity"
    )
    assigned_partner = models.ForeignKey(
        Partner,
        verbose_name="Colaborador associado",
        related_name="opportunity_assigned_partner",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    assigned_date = models.DateTimeField(
        verbose_name="Data de associação",
        help_text="Data e hora da última associação de colaborador",
        blank=True,
        null=True,
    )
    pipeline = models.ForeignKey(
        PipelineItem, verbose_name="pipeline", on_delete=CASCADE
    )
    campaign = models.ForeignKey(
        CrmCampaignUnity,
        verbose_name="campanha",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    source = models.ForeignKey(
        CrmCustomerSource,
        verbose_name="origem",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    main_unit = models.ForeignKey(
        CorporateGroupUnity,
        on_delete=CASCADE,
        blank=True,
        null=True,
        verbose_name="Unidade principal",
    )
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    absent = models.BooleanField(verbose_name="Ausente?", default=False)
    whatsapp_chat_id = models.CharField(
        verbose_name="Id da conversa no Whatsapp",
        null=True,
        max_length=255,
    )

    class Meta:
        managed = False
        ordering = ["-assigned_date"]
        db_table = "crm_opportunity"


class CRMLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    opportunity = models.ForeignKey(
        Opportunity, verbose_name="Oportunidade", on_delete=CASCADE, related_name="logs"
    )
    activity = models.PositiveIntegerField(verbose_name="Atividade")
    collaborator = models.ForeignKey(
        Partner,
        verbose_name="Colaborador associado",
        related_name="crm_logs",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    description = models.CharField(verbose_name="Descrição", max_length=500)
    date_and_time = models.DateTimeField(verbose_name="Data e hora")
    # pipeline = models.ForeignKey(
    #     PipelineItem,
    #     verbose_name="Pipeline",
    #     on_delete=CASCADE,
    #     null=True,
    #     blank=True,
    # )
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "crm_log"
        ordering = ["-created_on"]


class SalesOrderSkuBalance(models.Model):
    EXECUTION = "execution"
    DISCOUNT = "discount"
    SCHEDULING = "scheduling"
    ENTRY = "entry"
    SCHEDULING_CANCELLED = "scheduling_cancelled"
    EXECUTION_CANCELLED = "execution_cancelled"

    REASON_TYPE_CHOICES = [
        (EXECUTION, "Execução"),
        (DISCOUNT, "Desconto"),
        (SCHEDULING, "Agendamento"),
        (ENTRY, "Entrada"),
        (SCHEDULING_CANCELLED, "Agendamento Cancelado"),
        (EXECUTION_CANCELLED, "Execução Cancelada"),
    ]

    EXIT = "exit"
    ENTRY = "entry"

    MOVEMENT_TYPE_CHOICES = [
        (EXIT, "Saída"),
        (ENTRY, "Entrada"),
    ]
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    sales_order_sku = models.ForeignKey(
        "SalesOrderSku",
        on_delete=RESTRICT,
        null=False,
        verbose_name="SKU da Venda",
        related_name="sales_order_sku",
    )
    reason = models.CharField(
        max_length=120,
        verbose_name="Motivo da Movimentação",
    )
    reason_type = models.CharField(
        max_length=30, verbose_name="Tipo do Motivo", choices=REASON_TYPE_CHOICES
    )
    movement_type = models.CharField(
        max_length=30,
        verbose_name="Tipo de Movimentação",
        choices=MOVEMENT_TYPE_CHOICES,
    )
    quantity = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name="Quantidade da Movimentação",
    )
    description = models.CharField(
        max_length=120,
        verbose_name="Descrição da Movimentação",
    )
    sales_order_sku_replacement = models.ForeignKey(
        "SalesOrderSku",
        on_delete=RESTRICT,
        null=True,
        verbose_name="SalesOrderSku que gerou a reposição",
        related_name="sales_order_sku_replacement",
    )
    schedule = models.ForeignKey(
        "Schedule",
        on_delete=RESTRICT,
        null=True,
        verbose_name="Agendamento referente a movimentação",
    )
    migration = models.BooleanField(
        verbose_name="Foi migrado?",
        default=False,
    )
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "sales_order_sku_balance"
        ordering = ["id"]


class Document(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
    )
    observations = models.CharField(
        max_length=150, blank=True, null=True, default="", verbose_name="Observações"
    )
    document_type = models.CharField(
        max_length=100,
        verbose_name="Tipo do Documento",
    )
    body = TextField(default="", verbose_name="Documento em formato HTML")
    corporate_group_unity = models.ForeignKey(
        CorporateGroupUnity,
        blank=True,
        null=True,
        on_delete=CASCADE,
        verbose_name="Unidade",
        help_text="Unidade do grupo corporativo",
    )

    class Meta:
        managed = False
        db_table = "documents"
        ordering = ["id"]


class DocumentHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    document = models.ForeignKey(
        Document,
        on_delete=CASCADE,
        verbose_name="Documento",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome",
    )
    observations = models.CharField(
        max_length=150, blank=True, null=True, default="", verbose_name="Observações"
    )
    document_type = models.CharField(
        max_length=100,
        verbose_name="Tipo do Documento",
    )
    body = TextField(max_length=5000, default="", verbose_name="Observações")

    class Meta:
        managed = False
        db_table = "document_history"
        ordering = ["id"]


class PartnerCustomerDocumentSale(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_on = models.DateTimeField()
    last_edit_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()
    is_template = models.BooleanField()
    created_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    last_edit_by = models.ForeignKey(
        "AccessUser", models.DO_NOTHING, blank=True, null=True
    )
    document_type = models.CharField(max_length=30, verbose_name="Tipo de Documento")
    document = models.ForeignKey(
        Document,
        verbose_name="Documento associado",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    document_version = models.ForeignKey(
        "DocumentHistory",
        verbose_name="Versão do documento associado",
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    sales_order = models.ForeignKey(SalesOrder, on_delete=CASCADE, null=True)
    customer = models.ForeignKey(Partner, on_delete=CASCADE, null=True)
    corporate_group = models.ForeignKey("CorporateGroup", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "partner_customer_document_sale"
        ordering = ["id"]
