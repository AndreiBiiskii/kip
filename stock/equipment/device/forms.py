import datetime
import re

from django.http import request

from device.variables import *
from dateutil.relativedelta import relativedelta
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render, redirect

from .models import *


class ChangFields(forms.ModelForm):
    tag = forms.CharField(max_length=200, initial=forms.Form.base_fields)

    def clean(self):
        cleaned_data = super().clean()
        tag = cleaned_data.get('tag')
        if tag:
            if Tag.objects.filter(name=tag).exists():
                raise ValidationError('Такой тег уже существует.')
        return cleaned_data


class AddEquipmentForm(forms.Form):
    serial_number = forms.CharField(label='Серийный номер', max_length=100)
    model = forms.ModelChoiceField(label='Модель:', queryset=EquipmentModel.objects.all(), required=False)
    model_new = forms.CharField(label='Добавить модель:', required=False)
    type = forms.ModelChoiceField(label='Тип оборудования:', queryset=EquipmentType.objects.all(), required=False)
    type_new = forms.CharField(label='Добавить тип:', max_length=15, required=False)
    manufacturer = forms.ModelChoiceField(label='Производитель:', queryset=Manufacturer.objects.all(), required=False)
    manufacturer_new = forms.CharField(label='Добавить производителя:', required=False)
    name = forms.ModelChoiceField(queryset=EquipmentName.objects.all(), required=False, label='Наименование:')
    name_new = forms.CharField(label='Добавить наименование:', required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={"cols": "20", 'rows': "10"}), label='Комментарий:')
    position = forms.ModelChoiceField(queryset=GP.objects.all(), label='Поз. по ГП')
    location = forms.CharField(widget=forms.TextInput, max_length=50, required=False)
    tag = forms.CharField(label='Тег', max_length=100)
    status = forms.ModelChoiceField(label='Статус:', queryset=StatusAdd.objects.all(), required=False)
    status_new = forms.CharField(label='Добавить статус', max_length=10, required=False)
    year = forms.ModelChoiceField(label='Год выпуска:', queryset=Year.objects.all(), required=False)

    def clean(self):
        if Equipment.objects.filter(serial_number=self.cleaned_data['serial_number'],
                                    model=self.cleaned_data['model']):
            raise forms.ValidationError(message='Оборудование уже есть.')
        if (self.cleaned_data['model'] is None) & (self.cleaned_data['model_new'] == ''):
            raise forms.ValidationError(message='Не указана модель.')
        if len(self.cleaned_data['model_new']) > 100:
            raise forms.ValidationError(message='Модель должен быть до 100 символов.')
        if (self.cleaned_data['manufacturer'] is None) & (self.cleaned_data['manufacturer_new'] == ''):
            raise forms.ValidationError(message='Не указан производитель.')
        if len(self.cleaned_data['manufacturer_new']) > 100:
            raise forms.ValidationError(message='Производитель должен быть до 100 символов.')
        if (self.cleaned_data['name'] is None) & (self.cleaned_data['name_new'] == ''):
            raise forms.ValidationError(message='Не указано наименование.')
        if len(self.cleaned_data['name_new']) > 100:
            raise forms.ValidationError(message='Наименование должно быть до 100 символов')
        if self.cleaned_data['year'] is None:
            raise forms.ValidationError(message='Не указан год выпуска.')
        if self.cleaned_data['year'].name > datetime.datetime.now().year:
            raise forms.ValidationError(message='Год выпуска не может быть больше текущего')
        if (self.cleaned_data['status'] is None) & (self.cleaned_data['status_new'] == ''):
            raise forms.ValidationError(message='Не указан статус.')
        if (self.cleaned_data['type'] is None) & (self.cleaned_data['type_new'] == ''):
            raise forms.ValidationError(message='Не указан тип оборудования.')
        if 100 > len(self.cleaned_data['description']) < 10:
            raise forms.ValidationError(message='Комментарий должен быть от 10 до 100 символов.')
        return self.cleaned_data

    def save(self, user):
        description = self.cleaned_data.pop('description')
        if len(description) < 5:
            raise forms.ValidationError(message='Добавьте описание.')
        position = self.cleaned_data.pop('position')
        location = self.cleaned_data.pop('location')
        tag = self.cleaned_data.pop('tag')
        self.cleaned_data['si_or'] = False
        if self.cleaned_data['type_new']:
            self.cleaned_data['type'] = self.cleaned_data['type_new']
        if self.cleaned_data['manufacturer_new']:
            self.cleaned_data['manufacturer'] = self.cleaned_data['manufacturer_new']
        if self.cleaned_data['name_new']:
            self.cleaned_data['name'] = self.cleaned_data['name_new']
        if self.cleaned_data['model_new']:
            self.cleaned_data['model'] = self.cleaned_data['model_new']
        if self.cleaned_data['status_new']:
            self.cleaned_data['status'] = self.cleaned_data['status_new']

        EquipmentType.objects.get_or_create(name=self.cleaned_data['type'])
        Manufacturer.objects.get_or_create(name=self.cleaned_data['manufacturer'])
        EquipmentName.objects.get_or_create(name=self.cleaned_data['name'])
        EquipmentModel.objects.get_or_create(name=self.cleaned_data['model'])
        StatusAdd.objects.get_or_create(name=self.cleaned_data['status'])
        equipment = Equipment.objects.create(serial_number=self.cleaned_data['serial_number'],
                                             type=EquipmentType.objects.get(name=self.cleaned_data['type']),
                                             manufacturer=Manufacturer.objects.get(
                                                 name=self.cleaned_data['manufacturer']),
                                             name=EquipmentName.objects.get(name=self.cleaned_data['name']),
                                             model=EquipmentModel.objects.get(name=self.cleaned_data['model']),
                                             year=Year.objects.get(name=self.cleaned_data['year'].name),
                                             si_or=False,
                                             )
        status = StatusAdd.objects.get(name=self.cleaned_data['status'])
        Status.objects.create(equipment=equipment, name=status)
        Tag.objects.create(equipment=equipment, name=tag)
        Location.objects.create(equipment=equipment, name=location)
        Position.objects.create(equipment=equipment, name=position)
        Description.objects.create(equipment=equipment, user=user, name=description)
        return self.cleaned_data


class AddDeviceForm(forms.Form):
    serial_number = forms.CharField(label='Серийный номер:', max_length=100)
    model = forms.ModelChoiceField(label='Модель:', queryset=EquipmentModel.objects.all(), required=False)
    model_new = forms.CharField(label='Добавить модель:', required=False)
    type = forms.ModelChoiceField(label='Тип оборудования:', queryset=EquipmentType.objects.all(), required=False)
    type_new = forms.CharField(label='Добавить тип:', max_length=15, required=False)
    manufacturer = forms.ModelChoiceField(label='Производитель:', queryset=Manufacturer.objects.all(), required=False)
    manufacturer_new = forms.CharField(label='Добавить производителя:', required=False)
    name = forms.ModelChoiceField(queryset=EquipmentName.objects.all(), required=False, label='Наименование:')
    name_new = forms.CharField(label='Добавить наименование:', required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={"cols": "20", 'rows': "10"}), label='Комментарий:')
    position = forms.ModelChoiceField(queryset=GP.objects.all(), label='Поз. по ГП')
    location = forms.CharField(label='Место установки:', max_length=20, required=False)
    tag = forms.CharField(label='Тег', max_length=10, required=False)
    status = forms.ModelChoiceField(label='Статус:', queryset=StatusAdd.objects.all(), required=False)
    status_new = forms.CharField(label='Добавить статус', max_length=10, required=False)
    year = forms.ModelChoiceField(label='Год выпуска:', queryset=Year.objects.all(), required=False)
    # error = forms.ModelChoiceField(label='Погрешность:', queryset=Error.objects.all(), required=False)
    # error_new = forms.CharField(label='Добавить погрешность:', required=False)
    reg_number = forms.ModelChoiceField(label='Регистрационный номер:', queryset=RegNumber.objects.all(),
                                        required=False)
    reg_number_new = forms.CharField(label='Добавить регистрационный номер:', max_length=20, required=False)
    previous_verification = forms.DateField(label='Дата предыдущей поверки:', widget=forms.TextInput(attrs=
    {
        'type': 'date',
        'value': datetime.date.today().strftime('%Y-%m-%d'),
    }))
    certificate = forms.CharField(widget=forms.TextInput(attrs={"size": "50"}), label='Сертификат:')
    interval = forms.ChoiceField(label='Межповерочный интервал:', choices=CHOICES_INTERVAL)
    min_scale = forms.DecimalField(label='Мин. шкалы:')
    max_scale = forms.DecimalField(label='Макс. шкалы:')
    unit = forms.ChoiceField(label='Единицы измерения:', choices=CHOICES_UNIT)

    def clean(self):
        if Equipment.objects.filter(serial_number=self.cleaned_data['serial_number'],
                                    model=self.cleaned_data['model']):
            raise forms.ValidationError(message='Оборудование уже есть.')
        if (self.cleaned_data['model'] is None) & (self.cleaned_data['model_new'] == ''):
            raise forms.ValidationError(message='Не указана модель.')
        if len(self.cleaned_data['model_new']) > 100:
            raise forms.ValidationError(message='Модель должен быть до 100 символов.')
        if (self.cleaned_data['manufacturer'] is None) & (self.cleaned_data['manufacturer_new'] == ''):
            raise forms.ValidationError(message='Не указан производитель.')
        if len(self.cleaned_data['manufacturer_new']) > 100:
            raise forms.ValidationError(message='Производитель должен быть до 100 символов.')
        if (self.cleaned_data['name'] is None) & (self.cleaned_data['name_new'] == ''):
            raise forms.ValidationError(message='Не указано наименование.')
        if len(self.cleaned_data['name_new']) > 100:
            raise forms.ValidationError(message='Наименование должно быть до 100 символов')
        if self.cleaned_data['year'] is None:
            raise forms.ValidationError(message='Не указан год выпуска.')
        if self.cleaned_data['year'].name > datetime.datetime.now().year:
            raise forms.ValidationError(message='Год выпуска не может быть больше текущего')
        if (self.cleaned_data['status'] is None) & (self.cleaned_data['status_new'] == ''):
            raise forms.ValidationError(message='Не указан статус.')
        # if (self.cleaned_data['error'] is None) & (self.cleaned_data['error_new'] == ''):
        #     raise forms.ValidationError(message='Не указана погрешность.')
        if (self.cleaned_data['name'] is None) & (self.cleaned_data['name_new'] == ''):
            raise forms.ValidationError(message='Не указано наименование.')
        if (self.cleaned_data['type'] is None) & (self.cleaned_data['type_new'] == ''):
            raise forms.ValidationError(message='Не указан тип оборудования.')
        if (self.cleaned_data['reg_number'] is None) & (self.cleaned_data['reg_number_new'] == ''):
            raise forms.ValidationError(message='Не указан регистрационный номер.')
        if len(self.cleaned_data['reg_number_new']) < 5:
            raise forms.ValidationError(message='Регистрационный номер должен быть не менее 5 символов.')
        if 100 > len(self.cleaned_data['description']) < 10:
            raise forms.ValidationError(message='Комментарий должен быть от 10 до 100 символов.')
        return self.cleaned_data

    def save(self, user):
        description = self.cleaned_data.pop('description')
        position = self.cleaned_data.pop('position')
        location = self.cleaned_data.pop('location')
        tag = self.cleaned_data.pop('tag')
        min_scale = self.cleaned_data.pop('min_scale')
        max_scale = self.cleaned_data.pop('max_scale')
        previous_verification = self.cleaned_data.pop('previous_verification')
        certificate = self.cleaned_data.pop('certificate')
        if self.cleaned_data['type_new']:
            self.cleaned_data['type'] = self.cleaned_data['type_new']
        if self.cleaned_data['manufacturer_new']:
            self.cleaned_data['manufacturer'] = self.cleaned_data['manufacturer_new']
        if self.cleaned_data['name_new']:
            self.cleaned_data['name'] = self.cleaned_data['name_new']
        if self.cleaned_data['model_new']:
            self.cleaned_data['model'] = self.cleaned_data['model_new']
        if self.cleaned_data['status_new']:
            self.cleaned_data['status'] = self.cleaned_data['status_new']
        # if self.cleaned_data['error_new']:
        #     self.cleaned_data['error'] = self.cleaned_data['error_new']
        if self.cleaned_data['reg_number_new']:
            self.cleaned_data['reg_number'] = self.cleaned_data['reg_number_new']
        EquipmentType.objects.get_or_create(name=self.cleaned_data['type'])
        Manufacturer.objects.get_or_create(name=self.cleaned_data['manufacturer'])
        EquipmentName.objects.get_or_create(name=self.cleaned_data['name'])
        EquipmentModel.objects.get_or_create(name=self.cleaned_data['model'])
        StatusAdd.objects.get_or_create(name=self.cleaned_data['status'])
        equipment = Equipment.objects.create(serial_number=self.cleaned_data['serial_number'],
                                             type=EquipmentType.objects.get(name=self.cleaned_data['type']),
                                             manufacturer=Manufacturer.objects.get(
                                                 name=self.cleaned_data['manufacturer']),
                                             name=EquipmentName.objects.get(name=self.cleaned_data['name']),
                                             model=EquipmentModel.objects.get(name=self.cleaned_data['model']),
                                             year=Year.objects.get(name=self.cleaned_data['year'].name),

                                             )
        status = StatusAdd.objects.get(name=self.cleaned_data['status'])
        Status.objects.create(equipment=equipment, name=status)
        Tag.objects.create(equipment=equipment, name=tag)
        Location.objects.create(equipment=equipment, name=location)
        Position.objects.create(equipment=equipment, name=position)
        Description.objects.create(equipment=equipment, user=user, name=description)
        VerificationInterval.objects.get_or_create(name=self.cleaned_data['interval'])
        Scale.objects.get_or_create(min_scale=min_scale, max_scale=max_scale)
        # Error.objects.get_or_create(name=self.cleaned_data['error'])
        RegNumber.objects.get_or_create(name=self.cleaned_data['reg_number'])
        Unit.objects.get_or_create(name=self.cleaned_data['unit'])
        Si.objects.create(equipment=equipment,
                          previous_verification=previous_verification,
                          next_verification=previous_verification + relativedelta(
                              months=+(int(self.cleaned_data['interval']))),
                          certificate=certificate,
                          interval=VerificationInterval.objects.get(name=self.cleaned_data['interval']),
                          scale=Scale.objects.get(min_scale=min_scale, max_scale=max_scale),
                          unit=Unit.objects.get(name=self.cleaned_data['unit']),
                          # error_device=Error.objects.get(name=self.cleaned_data['error']),
                          reg_number=RegNumber.objects.get(name=self.cleaned_data['reg_number']))
        return self.cleaned_data


class SearchForm(forms.Form):
    serial_number = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))


class DraftForm(forms.ModelForm):
    class Meta(object):
        model = Draft
        exclude = ('user_draft',)


class DraftFormDevice(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '4', 'cols': '80'}))


class FormFilter(forms.Form):
    search = forms.ModelChoiceField(queryset=EquipmentType.objects.all())
