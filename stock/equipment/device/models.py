from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class StatusAdd(models.Model):
    name = models.CharField(max_length=50, verbose_name='Статус', unique=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.ForeignKey(StatusAdd, on_delete=models.DO_NOTHING, related_name='statuses', verbose_name='Статус')
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING, related_name='status',
                                  verbose_name='Статус')

    def __str__(self):
        return self.equipment

    class Meta:
        ordering = ('equipment',)


# class Category(models.Model):
#     name = models.CharField(max_length=50, verbose_name='Категория', unique=True)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = 'Категории'


class VerificationInterval(models.Model):
    name = models.CharField(max_length=4, verbose_name='Межповерочный интервал')

    # interval = models.OneToOneField('Equipment', on_delete=models.DO_NOTHING, related_name='interval')

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=255, verbose_name='Производитель оборудования', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Производители'


class EquipmentType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тип оборудования', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Типы оборудования'


class EquipmentModel(models.Model):
    name = models.CharField(max_length=255, verbose_name='Модель оборудования', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Модели оборудования'


class EquipmentName(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование оборудования', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Наименование оборудования'


class Position(models.Model):
    name = models.CharField(verbose_name='Позиция по ГП', blank=True, null=True)
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING, related_name='positions')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Позиции'
        ordering = ('-equipment',)


class Description(models.Model):
    name = models.CharField(max_length=100, verbose_name='Описание', blank=False, null=False)
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING, verbose_name='Описание оборудования',
                                  related_name='descriptions')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='descriptions',
                             verbose_name='Пользователь')
    at_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.equipment

    class Meta:
        verbose_name_plural = 'Описания оборудования'


class Location(models.Model):
    name = models.CharField(max_length=255, verbose_name='Место нахождения.', blank=True, null=True)
    equipment = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING, related_name='locations',
                                  verbose_name='Место установки', default='NoneLocation')

    def __str__(self):
        return self.equipment

    class Meta:
        verbose_name_plural = 'Места установки'


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Тэг', blank=True, null=True)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, related_name='tags', verbose_name='Тэг',
                                  default='NoneTag')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Тэг'


class Equipment(models.Model):
    serial_number = models.CharField(max_length=25, verbose_name='Серийный номер')
    model = models.ForeignKey(EquipmentModel, on_delete=models.CASCADE, related_name='model', blank=True, null=True)
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    defect = models.BooleanField(default=False, blank=True, null=True)
    si_or = models.BooleanField(default=True, verbose_name='Средство измерения или нет')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='manufacturer',
                                     verbose_name='Производитель')
    type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, related_name='type',
                             verbose_name='Тип', default=None, null=True)
    name = models.ForeignKey(EquipmentName, on_delete=models.CASCADE, related_name='n',
                             verbose_name='Наименование оборудования')
    year = models.ForeignKey('Year', on_delete=models.DO_NOTHING, related_name='years', verbose_name='Год выпуска')

    def __str__(self):
        return self.serial_number

    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'pk': self.pk})

    class Meta:
        unique_together = ('serial_number', 'model')
        verbose_name_plural = 'Оборудование'
        ordering = ('-at_date',)


class Si(models.Model):
    equipment = models.ForeignKey(Equipment, blank=True, null=True, on_delete=models.DO_NOTHING,
                                  related_name='si',
                                  verbose_name='Средство измерения')
    previous_verification = models.DateField(verbose_name='Дата предыдущей поверки')
    next_verification = models.DateField(verbose_name='Дата следующей поверки')
    certificate = models.CharField(max_length=100, verbose_name='Свидетельство о поверке', default='еще нет')
    interval = models.ForeignKey(VerificationInterval, on_delete=models.CASCADE, related_name='interval', blank=True,
                                 null=True, verbose_name='Межповерочный интервал (мес)')
    scale = models.ForeignKey('Scale', on_delete=models.CASCADE, related_name='scale', verbose_name='Шкала датчика')
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit', verbose_name='Единица измерения')
    # error_device = models.ForeignKey('Error', on_delete=models.DO_NOTHING, related_name='error_device',
    #                                  verbose_name='Погрешность', default=1)
    reg_number = models.ForeignKey('RegNumber', on_delete=models.DO_NOTHING, related_name='reg_number',
                                   verbose_name='Регистрационный номер')
    result = models.BooleanField(default=True)

    # def __str__(self):
    #     return self.equipment.name

    class Meta:
        verbose_name_plural = 'Средства измерения'

    # def get_absolute_url(self):
    #     return reverse('si_detail', kwargs={'pk': self.pk})


class Draft(models.Model):
    poz_draft = models.ForeignKey('GP', on_delete=models.CASCADE, blank=False, null=False, verbose_name='Поз. по ГП')
    location_draft = models.CharField(max_length=150, blank=False, null=False, verbose_name='Место установки')
    tag_draft = models.CharField(max_length=150, blank=False, null=False, verbose_name='Тэг')
    description_draft = models.CharField(max_length=150, blank=False, null=False, verbose_name='Описание')
    status_draft = models.ForeignKey(StatusAdd, on_delete=models.CASCADE, blank=False, null=False,
                                     verbose_name='Статус')
    images = models.ImageField(blank=False, null=False, verbose_name='Фото', upload_to='images')
    user_draft = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.poz_draft.name

    def get_absolute_url(self):
        return reverse('draft_detail', kwargs={'pk': self.pk})


class GP(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name='Позиция по ГП')
    construction = models.CharField(max_length=100, blank=True, verbose_name='Наименование здания, сооружения')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name',]


class RegNumber(models.Model):
    name = models.CharField(max_length=10, verbose_name='Регистрационный номер')

    def __str__(self):
        return self.name


# class Error(models.Model):
#     name = models.CharField(max_length=10, verbose_name='Погрешность')
#
#     def __str__(self):
#         return self.name


class Year(models.Model):
    name = models.SmallIntegerField(validators=[MaxValueValidator(2045), MinValueValidator(2020)],
                                    verbose_name='Год выпуска')

    def __str__(self):
        return str(self.name)


class Scale(models.Model):
    min_scale = models.CharField(max_length=10, verbose_name='Минимум шкалы')
    max_scale = models.CharField(max_length=10, verbose_name='Максимум шкалы')


class Unit(models.Model):
    name = models.CharField(max_length=10, verbose_name='Единицы измерения')

    def __str__(self):
        return self.name


class Defect(models.Model):
    defect = models.ForeignKey(Equipment, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='equipment')
    defect_act = models.CharField(max_length=20, verbose_name='Номер деффектного акта', blank=True, null=True,
                                  unique=True)
    project = models.CharField(max_length=100, verbose_name='Наименование проекта')
    short_description = models.TextField(verbose_name='Краткое описание деффекта')
    causes = models.TextField(verbose_name='Причина отказа')
    models.TextField(verbose_name='Что требуется для устранения')
    operating_time = models.SmallIntegerField(verbose_name='Время наработки')
    invest_letter = models.CharField(max_length=255, verbose_name='Номер письма в Инвест')

    approve = models.ForeignKey('Approve', on_delete=models.DO_NOTHING, related_name='approve',
                                verbose_name='Утверждающий')
    contractor = models.ForeignKey('Contractor', on_delete=models.DO_NOTHING, related_name='contractor',
                                   verbose_name='Подрядчик')
    kait = models.ForeignKey('Kait', on_delete=models.DO_NOTHING, related_name='kait', verbose_name='Мастер по КАиТ')
    worker = models.ForeignKey('Worker', on_delete=models.DO_NOTHING, related_name='worker', verbose_name='Мастер цеха')


# class DefectAct(models.Model):
#     defect_act = models.CharField(max_length=20, verbose_name='Номер деффектного акта')
#     defect_act = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='acts')
#
#     def __str__(self):
#         return self.name
#
#
# class Project(models.Model):
#     name = models.CharField(max_length=100, verbose_name='Наименование проекта')
#     project = models.OneToOneField(Equipment, on_delete=models.DO_NOTHING, related_name='project')
#
#     def __str__(self):
#         return self.name
#
#
# class DateCreate(models.Model):
#     name = models.DateField(verbose_name='Дата внесения записи дефекта')
#
#     # date_create = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='created')
#
#     def __str__(self):
#         return str(self.name)
#
#
# class ShortDescription(models.Model):
#     name = models.TextField(verbose_name='Краткое описание деффекта')
#     short_description = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='short_descriptions')
#
#     def __str__(self):
#         return self.name
#
#
# class Causes(models.Model):
#     name = models.TextField(verbose_name='Причина отказа')
#     causes = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='causes')
#
#     def __str__(self):
#         return self.name
#
#
# class Fix(models.Model):
#     name = models.TextField(verbose_name='Что требуется для устранения')
#     fix = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='fixes')
#
#     def __str__(self):
#         return self.name
#
#
# class OperatingTime(models.Model):
#     name = models.SmallIntegerField(verbose_name='Время наработки')
#     operating_time = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='operating_times')
#
#     def __str__(self):
#         return self.name
#
#
# class InvestLetter(models.Model):
#     name = models.CharField(max_length=255, verbose_name='Номер письма в Инвест')
#     invest_letter = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='invest_letters')
#
#     def __str__(self):
#         return self.name


class Approve(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО утв.', unique=True)
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')

    # approve = models.ForeignKey(Equipment, on_delete=.DO_NOTHING, related_name='approves', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Утверждающие'


class Contractor(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО подряднчика', unique=True)
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')

    # contractor = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='contractors', blank=True,
    # null = True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Подрядные организации'


class Kait(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО мастера Каит', unique=True)
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')

    # kait = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='kaits', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Мастера КАиТ'
        ordering = ('-job_title',)


class Worker(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО мастера цеха', unique=True)
    job_title = models.CharField(max_length=100, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')

    # worker = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='workers', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Мастера цеха'
