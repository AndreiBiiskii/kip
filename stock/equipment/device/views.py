import csv
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, DetailView, DeleteView, FormView
from rest_framework.permissions import IsAdminUser
from device.forms import AddEquipmentForm, AddDeviceForm, ChangFields, DraftForm, DraftFormDevice
from device.models import Equipment, GP, Si, EquipmentType, EquipmentModel, Manufacturer, Status, Position, \
    EquipmentName, Location, Tag, StatusAdd, Description, Year, Draft
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


def device(request):
    # with open('./new.csv', encoding='utf-8') as file2:
    #     with open('./new2.csv', 'w', encoding='utf-8') as file3:
    #         reader2 = csv.DictReader(file2, delimiter='|')
    #         headers = reader2.fieldnames
    #         writer = csv.DictWriter(file3, fieldnames=headers, delimiter='|')
    #         count1 = 0
    #         count2 = 0
    #         for item in reader2:
    #             with open('./si.csv', encoding='utf-8') as file1:
    #                 reader1 = csv.DictReader(file1, delimiter=';')
    #                 count1 += 1
    #                 for row in reader1:
    #                     count2 += 1
    #                     if item['serial_number'] in row['serial_number']:
    #                         item['certificate'] = row['certificate']
    #                         writer.writerow(item)
    #         print(count1, count2)
    with open('./GP.csv', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            GP.objects.create(name=row['number'], construction=row['construction'])

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
                    si__next_verification__lte=date_next)
                si_or = True
            data = {
                'si': si_or,
                'equipments': equipment,
                'title': 'Результаты поиска',
                'menu': menu,
            }
            if not equipment:
                data['error'] = 'Оборудование не найдено'
            return render(request, 'device/equipments.html', context=data)
        else:
            return render(request, 'device/equipments.html', {'menu': menu})
    else:
        return redirect('login')


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
