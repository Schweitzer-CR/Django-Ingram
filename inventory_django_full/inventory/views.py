from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import InventoryItem, InventoryLog
from .forms import InventoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


@login_required
def inventory_log(request):
    logs = InventoryLog.objects.select_related('user', 'item').order_by('-timestamp')
    return render(request, 'inventory/log.html', {'logs': logs})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('inventory')
    else:
        form = AuthenticationForm()
    return render(request, 'inventory/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'inventory/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def inventory_view(request):
    query = request.GET.get('q', '')
    if query:
        items = InventoryItem.objects.filter(part_number__icontains=query) | InventoryItem.objects.filter(description__icontains=query)
    else:
        items = InventoryItem.objects.all()
    return render(request, 'inventory/inventory.html', {'items': items, 'query': query})

@login_required
def add_item(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            item = form.save()
            InventoryLog.objects.create(
                user=request.user,
                item=item,
                change_type='add',
                quantity_before=None,
                quantity_after=item.quantity
            )
            return redirect('inventory')
    else:
        form = InventoryForm()
    return render(request, 'inventory/add_item.html', {'form': form})

from django.http import HttpResponse
from openpyxl import Workbook
from django.shortcuts import get_object_or_404

@login_required
def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    quantity_before = item.quantity
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            InventoryLog.objects.create(
                user=request.user,
                item=updated_item,
                change_type='edit',
                quantity_before=quantity_before,
                quantity_after=updated_item.quantity
            )
            return redirect('inventory')
    else:
        form = InventoryForm(instance=item)
    return render(request, 'inventory/add_item.html', {'form': form})


@login_required
@login_required
def delete_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        InventoryLog.objects.create(
            user=request.user,
            item=item,
            change_type='delete',
            quantity_before=item.quantity,
            quantity_after=0
        )
        item.delete()
        return redirect('inventory')
    return render(request, 'inventory/delete_confirm.html', {'item': item})

@login_required
def export_excel(request):
    items = InventoryItem.objects.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['Número de Parte', 'Descripción', 'Cantidad', 'Ubicación'])
    for item in items:
        ws.append([item.part_number, item.description, item.quantity, item.location])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    wb.save(response)
    return response

