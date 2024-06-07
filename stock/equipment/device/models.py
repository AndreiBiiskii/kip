from django.contrib.auth.models import User
from django.db import models

STATUS_CHOICES = {
    'rem': 'снят',
    'inst': 'установлен',
    'in_v': 'в поверку',
    'from_v': 'с поверки',
    'rep': 'ремонт',
    'def': 'дефектован',
}


class Status(models.Model):
    name = models.CharField(max_length=25, choices=STATUS_CHOICES, default='inst', verbose_name='Статус')
    status = models.ForeignKey('Equipment', on_delete=models.DO_NOTHING, related_name='status')


class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name='Оборудование/Прибор КИПиА')

    def __str__(self):
        return self.name


class VerificationInterval(models.Model):
    name = models.SmallIntegerField(verbose_name='Межповерочный интервал')
    interval = models.OneToOneField('Equipment', on_delete=models.DO_NOTHING, related_name='interval')

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=50, verbose_name='Производитель оборудования')

    def __str__(self):
        return self.name


class EquipmentType(models.Model):
    name = models.CharField(max_length=50, verbose_name='Тип оборудования')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Типы оборудования'


class EquipmentModel(models.Model):
    name = models.CharField(max_length=50, verbose_name='Модель оборудования')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Модели оборудования'


class EquipmentName(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование оборудования')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Наименование оборудования'


class Equipment(models.Model):
    serial_number = models.CharField(max_length=25, verbose_name='Серийный номер')
    model = models.OneToOneField(EquipmentModel, on_delete=models.DO_NOTHING, related_name='model')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    category = models.OneToOneField(Category, on_delete=models.DO_NOTHING, verbose_name='Категория',
                                    related_name='category')
    manufacturer = models.OneToOneField(Manufacturer, on_delete=models.DO_NOTHING, related_name='manufacturer')
    type = models.OneToOneField(EquipmentType, on_delete=models.DO_NOTHING, related_name='t')
    name = models.OneToOneField(EquipmentName, on_delete=models.DO_NOTHING, related_name='n')

    def __str__(self):
        return self.serial_number

    class Meta:
        verbose_name_plural = 'Оборудование'
        ordering = ('-at_date',)


class Position(models.Model):
    number = models.CharField(max_length=10, blank=False, verbose_name='Номер по генплану')
    construction = models.CharField(max_length=100, blank=True, verbose_name='Наименование здания, сооружения')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    position = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='positions')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name_plural = 'Позиции'
        ordering = ('-number',)


#
class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name='Место установки')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    equipment = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='locations')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Места установки'
        ordering = ('-at_date',)


class RealLocation(models.Model):
    name = models.CharField(max_length=50, verbose_name='Действительное место нахождения')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    location = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='reallocations')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Действительное место нахождения'
        ordering = ('-at_date',)


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Тэг')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    tag_d = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='tags')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Тэги'
        ordering = ('-at_date',)


class VerificationDate(models.Model):
    previous_verification = models.DateField(verbose_name='Дата предыдущей поверки')
    next_verification = models.DateField(verbose_name='Дата следующей поверки')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    verification_date = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='verifications')

    def __str__(self):
        return self.next_verification

    class Meta:
        verbose_name_plural = 'Даты поверок'
        ordering = ('-at_date',)


class Certificate(models.Model):
    name = models.CharField(max_length=100, verbose_name='Свидетельство о поверке')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    certificate = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='certificates')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Свидетельства о поверке'
        ordering = ('-at_date',)


class Description(models.Model):
    title = models.TextField(verbose_name='Описание ')
    user = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING, verbose_name='Кто внес данные')
    at_date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')
    description = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='descriptions')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Описания'
        ordering = ('-at_date',)


class DefectAct(models.Model):
    name = models.CharField(max_length=20, verbose_name='Номер деффектного акта')
    defect_act = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='acts')

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование проекта')
    project = models.OneToOneField(Equipment, on_delete=models.DO_NOTHING, related_name='project')

    def __str__(self):
        return self.name


class DateCreate(models.Model):
    name = models.DateField(verbose_name='Дата внесения записи деффекта')
    date_create = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='createds')

    def __str__(self):
        return str(self.date_create)


class ShortDescription(models.Model):
    name = models.TextField(verbose_name='Краткое описание деффекта')
    short_description = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='short_descriptions')

    def __str__(self):
        return self.name


class Causes(models.Model):
    name = models.TextField(verbose_name='Причина оказа')
    causes = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='causes')

    def __str__(self):
        return self.name


class Fix(models.Model):
    name = models.TextField(verbose_name='Что требуется для устранения')
    fix = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='fixes')

    def __str__(self):
        return self.name


class OperatingTime(models.Model):
    name = models.SmallIntegerField(verbose_name='Время наработки')
    operating_time = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='operating_times')

    def __str__(self):
        return self.name


class InvestLetter(models.Model):
    name = models.CharField(max_length=255, verbose_name='Номер письма в Инвест')
    invest_letter = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='invest_letters')

    def __str__(self):
        return self.name


class Approve(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО утв.')
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')
    approve = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='approves')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Утверждающие'


class Contractor(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО подряднчика')
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')
    contractor = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='contractors')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Подрядные организации'


class Kait(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО мастера Каит')
    job_title = models.CharField(max_length=50, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')
    kait = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='kaits')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Мастера КАиТ'
        ordering = ('-job_title',)


class Worker(models.Model):
    name = models.CharField(max_length=30, verbose_name='ФИО мастера цеха')
    job_title = models.CharField(max_length=100, verbose_name='Должность')
    organization = models.CharField(max_length=100, verbose_name='Организация')
    worker = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, related_name='workers')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Мастера цеха'
