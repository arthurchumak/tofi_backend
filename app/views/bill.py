# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.models import User, Card, Bill, Currency

from app.models import User, Card, Bill, Currency, Action


@login_required
def card(request, pk=None):
    pass


@login_required
@user_passes_test(lambda u: u.is_superuser)
def addcard(request, pk=None):
    if request.method == 'POST':
        try:
            pk = request.POST["num"]
            bill = Bill.objects.get(id=pk)
        except Bill.DoesNotExist:
            return redirect('client:list')

        bill.add_card(limit=request.POST['limit'])
        return redirect('client:list')

@login_required
def cards(request):
    try:
        _user = request.user
    except User.DoesNotExist:
        return redirect('index')

    cards = Card.objects.all().filter(bill__client_id=_user.id).order_by('bill_id')
    return render(request, 'bill/cards.html', {
        'cards': cards
    })


@login_required
def cardsinbill(request, pk):
    try:
        _bill = Bill.objects.get(id=pk)
    except Bill.DoesNotExist:
        return redirect('index')

    _cards = Card.objects.all().filter(bill=_bill)

    return render(request, 'bill/cardsinbill.html', {
        'cards': _cards,
        'bill': _bill
    })


@login_required
def bills(request):
    try:
        _user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return redirect('index')

    bills = Bill.objects.all().filter(client_id=_user.id).order_by('id')

    return render(request, 'bill/bills.html', {
        'bills': bills
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def addonbill(request, pk=None):
    if request.method == 'POST':
        try:
            pk = request.POST["num"]
            bill = Bill.objects.get(id=pk)
        except Bill.DoesNotExist:
            return redirect('client:list')

        pushmoney = int(request.POST['money'])
        bill.push(pushmoney)
        return redirect('client:list')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def addbill(request, pk=None):
    try:
        _user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return JsonResponse()

    if request.method == 'POST':
        try:
            currency = Currency.objects.get(title='BYN')
        except Currency.DoesNotExist:
            currency = Currency.objects.create(title='BYN', icon='p')

        _bill = _user.add_bill(currency=currency, money=0, is_private=True)
        return JsonResponse()


@login_required
def billoperations(request, pk=None):
    try:
        bill = Bill.objects.get(id=pk)
    except Bill.DoesNotExist:
        return redirect('bill:bills')

    if bill.client!=request.user:
        return redirect('errors:error')
    else:
        _operations=Action.objects.all().filter(bill=bill).order_by('-id')
        return render(request,'bill/billoperations.html',{
            'operations': _operations
        })


@login_required
def billtransact(request):
    if request.POST:
        try:
            _from = int(request.POST["_from"])
            _to = int(request.POST["_to"])

            frombill = Bill.objects.get(id=_from)
            tobill = Bill.objects.get(id=_to)

            if frombill == tobill:
                return render(request, 'bill/billtransact.html', {
                    'bills': Bill.objects.all().filter(client=request.user)
                })

            if frombill.client != request.user or tobill.client != request.user:
                return render(request, 'errors/error.html', {
                    'errors': u'Что-то пошло не так'
                })
            else:
                _money = int(request.POST["money"])
                if _money < frombill.money:
                    frombill.pop(_money)
                    tobill.push(_money)
                    return redirect('bill:bills')
                else:
                    return render(request, 'errors/error.html', {
                        'errors': u'Недостаточно средств'
                    })
        except:
            return render(request, 'errors/error.html', {
                'errors': u'Что-то пошло не так'
            })
    else:
        return render(request, 'bill/billtransact.html', {
            'bills': Bill.objects.all().filter(client=request.user)
        })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def getuserbills(request, pk=None):
    try:
        _user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return redirect('client:list')
    _bills = Bill.objects.all().filter(client=_user)
    _bills_id = []
    for a in _bills:
        _bills_id.append(a.id)
    if _bills:
        return JsonResponse({'bills': _bills_id})
    else:
        return redirect('client:list')