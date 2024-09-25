import csv
import datetime
import os

import django_filters
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView, FormView
from django_filters import filters
from rest_framework.permissions import IsAdminUser
from device.forms import AddEquipmentForm, AddDeviceForm, ChangFields, DraftForm, DraftFormDevice, FormFilter
from device.models import Equipment, GP, Si, EquipmentType, EquipmentModel, Manufacturer, Status, Position, \
    EquipmentName, Location, Tag, StatusAdd, Description, Year, Draft, VerificationInterval, Unit, RegNumber, Scale
from users.forms import LoginUserForm

menu = [
    {'title': 'Модели', 'url_name': 'models'},
    {'title': 'Производители', 'url_name': 'manufacturers'},
    {'title': 'Типы', 'url_name': 'types'},
    {'title': 'Названия', 'url_name': 'names'},
    {'title': 'Статусы', 'url_name': 'statuses'},
    {'title': 'Года выпуска', 'url_name': 'years'},
    {'title': 'Поиск', 'url_name': 'search'},
]


# position;location;teg;model;type ;name;reg_number;serial_number;year;min_scale;max_scale;unit;mpi;previous_verification;result;certificate
def si_loading(request):
    u = User.objects.get(username='admin')
    with open(os.path.join(settings.BASE_DIR, 'SIkgs.csv'), encoding='utf-8') as si:
        reader = csv.DictReader(si, delimiter=';')
        for i, row in enumerate(reader):
            if row['mpi'] == '':
                row['mpi'] = '0'
            if row['previous_verification'] == '':
                d = '{}-{}-{}'.format(1990, 1, 1)
            else:
                rez = row['previous_verification'].split('.')
                year = rez[2]
                month = rez[1]
                day = rez[0]
                d = '{}-{}-{}'.format(year, month, day)
            try:
                previous_verification = datetime.date.fromisoformat(d)
            except:
                previous_verification = datetime.datetime.fromisoformat('1990-01-01')

            next_verification = previous_verification + relativedelta(
                months=+(int(row['mpi'])))
            try:
                m = EquipmentModel.objects.get(name=row['model'])

            except:
                EquipmentModel.objects.create(name=row['model'])
            m = EquipmentModel.objects.get(name=row['model'])

            try:
                t = EquipmentType.objects.get(name=row['type'])
            except:
                EquipmentType.objects.create(name=row['type'])
            t = EquipmentType.objects.get(name=row['type'])

            try:
                n = EquipmentName.objects.get(name=row['name'])
            except:
                EquipmentName.objects.create(name=row['name'])
            n = EquipmentName.objects.get(name=row['name'])

            try:
                y = Year.objects.get(name=row['year'])
            except:
                Year.objects.create(name=row['year'])
            y = Year.objects.get(name=row['year'])

            try:
                man = Manufacturer.objects.get(name='manufacturer')
            except:
                Manufacturer.objects.create(name='manufacturer')
            man = Manufacturer.objects.get(name='manufacturer')
            try:
                eq = Equipment.objects.create(
                    serial_number=row['serial_number'],
                    model=m,
                    si_or=True,
                    manufacturer=man,
                    type=t,
                    name=n,
                    year=y,
                )
            except:
                continue

            Position.objects.create(name=row['position'], equipment=eq)
            Location.objects.create(name=row['location'], equipment=eq)
            Tag.objects.create(name=row['teg'], equipment=eq)
            Description.objects.create(name='description', equipment=eq, user=u)

            try:
                status = StatusAdd.objects.get(name='Установлен')
            except:
                StatusAdd.objects.create(name='Установлен')
            status = StatusAdd.objects.get(name='Установлен')

            Status.objects.create(name=status, equipment=eq)

            try:
                VerificationInterval.objects.get(name=row['mpi'])
            except:
                VerificationInterval.objects.create(name=row['mpi'])
            interval = VerificationInterval.objects.get(name=row['mpi'])

            try:
                Scale.objects.get(min_scale=row['min_scale'], max_scale=row['max_scale'])
            except:
                Scale.objects.create(min_scale=row['min_scale'], max_scale=row['max_scale'])
            scale = Scale.objects.get(min_scale=row['min_scale'], max_scale=row['max_scale'])

            try:
                Unit.objects.get(name=row['unit'])
            except:
                Unit.objects.create(name=row['unit'])
            unit = Unit.objects.get(name=row['unit'])

            try:
                RegNumber.objects.get(name=row['reg_number'])
            except:
                RegNumber.objects.create(name=row['reg_number'])
            reg_number = RegNumber.objects.get(name=row['reg_number'])

            Si.objects.create(
                equipment=eq,
                previous_verification=previous_verification,
                next_verification=next_verification,
                certificate=row['certificate'],
                interval=interval,
                scale=scale,
                unit=unit,
                reg_number=reg_number,
                result=True
            )
        return render(request, 'device/index.html')


def gp_loading(request):
    with open(os.path.join(settings.BASE_DIR, 'SIkgs.csv'), encoding='utf-8') as gp:
        reader = csv.DictReader(gp, delimiter=';')
        for row in reader:
            GP.objects.get_or_create(name=row['position'])
    with open(os.path.join(settings.BASE_DIR, 'SI.csv'), encoding='utf-8') as gp:
        reader = csv.DictReader(gp, delimiter=';')
        for row in reader:
            GP.objects.get_or_create(name=row['position'])

    return render(request, 'device/index.html')


def IM(request):
    with open('./im.csv') as f:
        readers = csv.DictReader(f, delimiter=';')
        i = 0
        for reader in readers:
            serial_number = reader['serial_number']
            EquipmentModel.objects.get_or_create(name=reader['model'])
            model = EquipmentModel.objects.get(name=reader['model'])
            user = request.user
            si = False
            Manufacturer.objects.get_or_create(name=reader['manufacturer'])
            manufacturer = Manufacturer.objects.get(name=reader['manufacturer'])
            EquipmentType.objects.get_or_create(name=reader['type'])
            t = EquipmentType.objects.get(name=reader['type'])
            Status.objects.get_or_create(name='Установлен')
            status = Status.objects.get(name='Установлен')
            Position.objects.get_or_create(name=reader['poz'])
            position = Position.objects.get(name=reader['poz'])
            EquipmentName.objects.get_or_create(name=reader['name'])
            name = EquipmentName.objects.get(name=reader['name'])
            Location.objects.get_or_create(name=reader['location'])
            location = Location.objects.get(name=reader['location'])
            Tag.objects.get_or_create(name=reader['tag'])
            tag = Tag.objects.get(name=reader['tag'])

            Equipment.objects.create(serial_number=serial_number, model=model, user=user, si=si,
                                     manufacturer=manufacturer, type=t, status=status, position=position,
                                     name=name, location=location, tag=tag)
            i += 1

        return render(request, 'device/index.html')


# def equipmentsL_lst(request):
#     model = Equipment
#     template_name = 'device/equipments.html'
#     fields = '__all__'
#     context_object_name = 'objects'
#     if not request.user.is_staff:
#         data = {
#             'objects': Equipment.objects.all()
#     }
#     return render(request, 'device/equipments.html', context=data)

def equipment_add(request):
    if request.method == 'POST':
        form = AddEquipmentForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('index')
    else:
        form = AddEquipmentForm()

    return render(request, 'device/equipment_add.html', {'form': form, 'menu': menu})


def device_add(request):
    if request.method == 'POST':
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('index')
    else:
        form = AddDeviceForm()
    return render(request, 'device/equipment_add.html', {'form': form, 'menu': menu})


def EquipmentUpdate(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    status = StatusAdd.objects.all()
    positions = GP.objects.all()
    data = {
        'equipment': equipment,
        'menu': menu,
        'status': status,
        'positions': positions,
        'si_or': False,
    }
    if request.method == 'POST':
        if request.POST['description'] != equipment.descriptions.last().name:
            Tag.objects.create(equipment=equipment, name=request.POST['tag'])
            Location.objects.create(equipment=equipment, name=request.POST['location'])
            Position.objects.create(equipment=equipment, name=request.POST['position'])
            Description.objects.create(equipment=equipment, user=request.user, name=request.POST['description'])
            status = StatusAdd.objects.get(name=request.POST['status'])
            Status.objects.create(equipment=equipment, name=status)
            return redirect('search')
        else:
            data['error'] = 'Комментарий не был изменен'

    return render(request, 'device/equipment_update.html', context=data)


def search(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            si = request.POST.get('si')
            tag = request.POST.get('tag')
            date_next = request.POST.get('date_next')
            serial_number = request.POST.get('serial_number')
            equipment = None
            si_or = False
            if ((serial_number != '') &
                    (si is None) & (tag == '') &
                    (not date_next)):  # только по серийному номеру
                si_or = False
                equipment = Equipment.objects.filter(
                    serial_number__icontains=serial_number)
            if (serial_number != '') & (si is not None):  # по серийному номеру и средству измерения
                si_or = True
                equipment = Equipment.objects.filter(Q(
                    serial_number__icontains=serial_number) & Q(si_or=si_or))
            if ((tag != '') & (si is None) &
                    (serial_number == '') &
                    (not date_next)):  # только по тегу
                si_or = False
                equipment = Equipment.objects.filter(
                    tags__name__icontains=tag)
            if (si is not None) & (not date_next):  # только средства измерения
                si_or = True
                equipment = Equipment.objects.filter(si_or=True)
            if date_next:
                equipment = Equipment.objects.filter(
                    si__next_verification__lte=date_next).order_by('-si__next_verification')
                si_or = True
            if request.method == 'POST':

                form = FormFilter(request.POST)

            else:
                form = FormFilter()

            data = {
                'si': si_or,
                'equipments': equipment,
                'title': 'Результаты поиска',
                'menu': menu,
                'formfilter': form,
            }
            if not equipment:
                data['error'] = 'Оборудование не найдено'
            return render(request, 'device/equipments.html', context=data)
        else:
            return render(request, 'device/equipments.html', {'menu': menu})
    else:
        return redirect('index')


class MyFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type__name', lookup_expr='contains', label='Тип:')
    position = django_filters.ModelChoiceFilter(queryset=GP.objects.all(), field_name='positions__name',
                                                lookup_expr='exact', label='Позиция:')
    name = django_filters.CharFilter(field_name='name__name', lookup_expr='contains', label='Название:')
    model = django_filters.CharFilter(field_name='model__name', lookup_expr='contains', label='Модель:')
    year__lt = django_filters.DateFilter(
        widget=forms.TextInput(attrs=
        {
            'type': 'date',
            # 'value': datetime.date.today().strftime('%Y-%m-%d'),
        }), label='Дата следующей поверки:'

        , field_name='si__next_verification', lookup_expr='lt'
    )
    status = django_filters.ModelChoiceFilter(queryset=StatusAdd.objects.all(), field_name='status__name',
                                              lookup_expr='exact', label='Статус')

    # year__gt = django_filters.DateFilter(
    #     widget=forms.TextInput(attrs=
    #     {
    #         'type': 'date',
    #         # 'value': datetime.date.today().strftime('%Y-%m-%d'),
    #     }), label='Дата следующей поверки:'
    #
    #     , field_name='si__next_verification', lookup_expr='gt'
    # )

    class Meta:
        model = Equipment
        fields = ['year', ]


def equipment_list(request):
    if request.method == 'POST':
        eq_filter = MyFilter(request.POST,
                             queryset=Equipment.objects.prefetch_related('si', 'status').all().order_by(
                                 '-si__next_verification'))
        data = {
            'title': 'Поиск',
            'menu': menu,
            'si': True,
            'equipments': eq_filter,
            'count': eq_filter.qs.count(),
        }
        return render(request, 'device/equipments.html', context=data)

    else:
        eq_filter = MyFilter(request.POST, queryset=Equipment.objects.all()[0:0])
        data = {
            'title': 'Поиск',
            'menu': menu,
            'si': True,
            'equipments': eq_filter,
        }

        return render(request, 'device/equipments.html', context=data)


def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    tag = equipment.tags.all()
    status = equipment.status.all()
    description = equipment.descriptions.all()
    location = equipment.locations.all()
    position = equipment.positions.all()
    statuses = []
    tags = []
    descriptions = []
    locations = []
    positions = []
    users = []
    data_eq = []
    at_date = []

    for i in position:
        positions.append(i.name)
    for i in status:
        statuses.append(i.name.name)
    for i in tag:
        tags.append(i.name)
    for i in description:
        descriptions.append(i.name)
        users.append(i.user)
        at_date.append(i.at_date)
    for i in location:
        locations.append(i.name)
    for i in range(len(descriptions)):
        data_eq.append({
            'description': descriptions[i],
            'tag': tags[i],
            'location': locations[i],
            'status': statuses[i],
            'position': positions[i],
            'user': users[i],
            'at_date': at_date[i],
        })
        data_eq.sort(key=lambda x: x['at_date'], reverse=True)
    data = {
        'equipment': equipment,
        'title': 'Информация об оборудовании',
        'menu': menu,
        'data_eq': data_eq,
    }
    return render(request, 'device/equipment_detail.html', context=data)


def DeviceUpdate(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    si = equipment.si.last()
    status = StatusAdd.objects.all()
    last_status = equipment.status.last()
    positions = GP.objects.all()
    last_position = equipment.positions.last()
    location = equipment.locations.last()
    description = equipment.descriptions.last()
    tag = equipment.tags.last()
    data = {
        'equipment': equipment,
        'menu': menu,
        'status': status,
        'last_status': last_status,
        'positions': positions,
        'last_position': last_position,
        'location': location,
        'description': description,
        'tag': tag,
        'si_or': True,
    }
    if request.method == 'POST':
        if len(request.POST['description']) < 10:
            data['error'] = 'Комментарий должен содержать не менее 10 символов'
            return render(request, 'device/equipment_update.html', context=data)
        if request.POST['description'] != equipment.descriptions.last().name:
            t = Tag(equipment=equipment, name=request.POST['tag'])
            l = Location(equipment=equipment, name=request.POST['location'])
            p = Position(equipment=equipment, name=request.POST['position'])
            d = Description(equipment=equipment, user=request.user, name=request.POST['description'])
            status = StatusAdd.objects.get(name=request.POST['status'])
            s = Status(equipment=equipment, name=status)
            t.save()
            l.save()
            p.save()
            d.save()
            s.save()
            si.previous_verification = request.POST['previous_verification']
            si.next_verification = (
                                       datetime.datetime.strptime(request.POST['previous_verification'],
                                                                  '%Y-%m-%d').date()) + relativedelta(
                months=+int(si.interval.name))
            si.certificate = request.POST['certificate']
            si.save()
            return redirect('search')
        else:
            data['error'] = 'Комментарий не был изменен'
    return render(request, 'device/equipment_update.html', context=data)


def EquipmentDelete(request, pk):
    if request.user.is_staff:
        obj = get_object_or_404(Equipment, pk=pk)
        obj.descriptions.all().delete()
        obj.positions.all().delete()
        obj.locations.all().delete()
        obj.tags.all().delete()
        obj.status.all().delete()
        obj.si.all().delete()
        obj.delete()
        return redirect('index')
    else:
        return redirect('index')


class AddCategory(CreateView):
    permission_classes = [IsAdminUser, ]
    template_name = 'device/add_category.html'
    fields = ['name']
    context_object_name = 'cats'
    success_url = '/'
    extra_context = {
        'menu': menu
    }


class ListCategory(ListView):
    template_name = 'device/list_category.html'
    context_object_name = 'objects'


class UpdateCategory(UpdateView):
    template_name = 'device/add_category.html'
    fields = ['name']
    context_object_name = 'cats'
    success_url = '/index'
    extra_context = {
        'menu': menu
    }


def delete_category(request, pk, Mod):
    obj = get_object_or_404(Mod, pk=pk)
    obj.delete()
    return render(request,
                  'device/index.html',
                  context={'error': 'Ошибка удаления, '
                                    'есть связи с оборудованием'})


def index(request):
    return render(request, 'device/index.html', {'menu': menu})


class LoginUser(LoginView):
    template_name = 'users/login.html'
    extra_context = {
        'title': 'Авторизация',
        'menu': menu,
    }
    form_class = AuthenticationForm


class ChangePassword(PasswordChangeView):
    template_name = 'users/change_password.html'
    extra_context = {
        'title': 'Изменение пароля',
        'menu': menu,
    }
    form_class = PasswordChangeForm
    success_url = '/'


def logout_user(request):
    logout(request)
    return redirect('users:login')


class DraftCreate(CreateView):
    form_class = DraftForm
    template_name = 'device/draft.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user_draft = self.request.user
        instance.save()
        return redirect('/')


class DraftList(ListView):
    model = Draft
    template_name = 'device/draft_list.html'
    context_object_name = 'drafts'
    queryset = Draft.objects.all()

    extra_context = {
        'title': 'Список черновиков',
        'menu': menu
    }


class DraftDetail(DetailView):
    model = Draft
    template_name = 'device/draft_detail.html'


def draft_device_add(request, pk):
    if request.method == 'POST':
        form = AddDeviceForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('index')
    else:
        form = AddDeviceForm()
    draft = Draft.objects.get(pk=pk)
    return render(request,
                  'device/equipment_add.html',
                  {'form': form, 'menu': menu,
                   'draft': draft,
                   'title': 'Изменение черновика'})


def draft_equipment_add(request, pk):
    if request.method == 'POST':
        form = AddEquipmentForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('index')
    else:
        form = AddEquipmentForm()
    draft = Draft.objects.get(pk=pk)
    return render(request,
                  'device/equipment_add.html',
                  {'form': form, 'menu': menu,
                   'draft': draft,
                   'title': 'Изменение черновика'})


def draft_delete(request, pk):
    if request.user.is_staff:
        obj = get_object_or_404(Draft, pk=pk)
        obj.delete()
        return redirect('index')
    else:
        return redirect('index')
