from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Sheet
from django.contrib.auth.decorators import login_required
from .forms import NewSheetForm
from django.contrib.auth.models import User
from .models import Data_Field
from django.contrib.auth import login as auth_login
from django.utils.safestring import mark_safe

import pandas as pd
from django.contrib import messages as alertmessage


@login_required
def newform(requests):
    form = NewSheetForm()

    if requests.method == 'POST' and 'Upload_Btn' in requests.POST:
        form = NewSheetForm(requests.POST, requests.FILES)
        if form.is_valid():
            sheet = form.save(commit=False)
            sku_dataframe = pd.read_excel(sheet.sheeturl)
            submitstatus, messages = dataframeduplicate(sku_dataframe)
            sku_dataframe = sku_dataframe[
                ['sku', 'store_view_code', 'creatorid', 'qualityid', 'isrejected']].values.tolist()
            # submitstatus, messages = checking_found(sku_dataframe)
            alertmessage.info(requests, mark_safe(messages))

    elif requests.method == 'POST' and 'Check_Files_Btn' in requests.POST:
        form = NewSheetForm(requests.POST, requests.FILES)
        if form.is_valid():
            sheet = form.save(commit=False)
            sku_dataframe = pd.read_excel(sheet.sheeturl)
            submitstatus2, messages2 = dataframeduplicate(sku_dataframe)

            sku_dataframe = sku_dataframe[
                ['sku', 'store_view_code', 'creatorid', 'qualityid', 'isrejected']].values.tolist()
            submitstatus, messages = checking_found(sku_dataframe)
            if not submitstatus or not submitstatus2:
                messages = messages2 + messages
                messages = str(messages.replace('\n', '<br />'))
                alertmessage.info(requests, mark_safe(messages))
            else:
                user = form.save(commit=False)
                user.Uploaderid = requests.user
                user.save()
                saving_sku(sku_dataframe, sheet.ticketname, sheet.batchNumber)
                return redirect('upload_done')

    return render(requests, 'index.html', {'form': form})


def saving_sku(sku_dataframe, ticketname, batchnumber):
    for item in sku_dataframe:
        data = Data_Field()
        data.SKU = item[0]
        data.Creatorid = get_object_or_404(User, username=item[1])
        data.Qualityid = get_object_or_404(User, username=item[2])
        data.isRejected = item[3]
        data.Sheetid = get_object_or_404(Sheet, ticketname=ticketname, batchNumber=batchnumber)
        data.save()


def checking_found(arr):
    skufoundlist, skunanlist, creatornotfoundlist, qualitynotfoundlist, isrejectednotfoundlist = ([] for _ in range(5))
    skufound = skunan = creatornotfound = qualitynotfound = isrejectednotfound = False
    # print(arr)
    for item in range(len(arr)):
        # check the existing sku
        try:
            # print(arr[item][0])
            sku = arr[item][0]
            if str(arr[item][1]) == 'ar':
                sku += '_ar'

            # print(sku)
            get_object_or_404(Data_Field, SKU=sku)
            # print('found')
            # print('safdd')
            skufound = True
            # print(1254)
            skufoundlist.append(str(item + 2))
            # print(14777)
        except:
            if str(arr[item][0]) == 'nan':
                skunan = True
                skunanlist.append(str(item + 2))

        # check not existing creator
        try:
            get_object_or_404(User, username=arr[item][2])
            pass
            # print(item+2)
        except:
            creatornotfound = True
            creatornotfoundlist.append(str(item + 2))
        # check not existing quality
        try:
            get_object_or_404(User, username=arr[item][3])
            pass
            # print(item+2)
        except:
            qualitynotfound = True
            qualitynotfoundlist.append(str(item + 2))
        # is rejected not boolean
        try:
            if str(arr[item][4]) == "nan":
                isrejectednotfound = True
                isrejectednotfoundlist.append(str(item + 2))

            # print(m)
        except:
            isrejectednotfound = True
            isrejectednotfoundlist.append(str(item + 2))

    submitbool = True
    message = ''
    if skunan:
        message += 'SKUs Not Found in row ' + '/'.join(skunanlist) + '\n'
        submitbool = False
    if skufound:
        message += 'Duplicate SKUs in row ' + '/'.join(skufoundlist) + '\n'
        submitbool = False
    if creatornotfound:
        message += 'Creatorid Not Found in row ' + '/'.join(creatornotfoundlist) + '\n'
        submitbool = False
    if qualitynotfound:
        message += 'Qualityid Not Found in row ' + '/'.join(qualitynotfoundlist) + '\n'
        submitbool = False
    if isrejectednotfound:
        message += 'Seif Value should be either 1 or 0 in row ' + '/'.join(isrejectednotfoundlist) + '\n'
        submitbool = False

    return submitbool, message


def done_upload(requests):
    return render(requests, 'success_upload.html')


def dataframeduplicate(df):
    boolean = df[['sku', 'store_view_code']].duplicated().any()
    # duplicate = df[df.duplicated(, keep='first')]

    if boolean:
        return False, 'There is Duplicate in SKUs of the Sheet \n'
    return True, ''

def search_skus(request):
    search_term = ''
    translation = ''
    articles = ''
    if 'search' in request.GET:
        search_term = request.GET['search']
        articles = Data_Field.objects.all().filter(SKU=search_term)
        data = search_term+'_ar'
        translation = Data_Field.objects.all().filter(SKU=data)

    # articles = Data_Field.objects.all()

    return render(request, 'Search_Sku.html', {'articles': articles, 'search_term': search_term,'translation':translation})


# return render(requests, 'Search_Sku.html')



def search_ticket_batch(request):
    search_term_ticket = ''
    translation =""
    articles = ""
    if 'search' in request.GET:


        search_term_ticket = request.GET['search']
        search_term_batch = request.GET['batch_search']
        # print(search_term_ticket,search_term_batch)
        articles = Sheet.objects.all().filter(ticketname=search_term_ticket,batchNumber=search_term_batch)
        print('byeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        print(articles,'\t',articles[0],'\t',articles[0].id)
        translation = Data_Field.objects.all().filter(Sheetid=articles[0].id).count
        print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii',translation)



    return render(request, 'Search_Ticket_Batch.html', {'articles': articles, 'search_term': search_term_ticket, 'translation': translation})


# return render(requests, 'Search_Sku.html')


def report_search(request):
    search_term = ''
    translation =''
    articles =''
    if 'search' in request.GET:
        search_term = request.GET['search']
        print(search_term)
        if str(search_term) =='all':
            articles = Data_Field.objects.all()
        else:
            articles = Data_Field.objects.all().filter(SKU=search_term)
        data = search_term+'_ar'
        translation = Data_Field.objects.all().filter(SKU=data)



    return render(request, 'Search_Sku.html', {'articles': articles, 'search_term': search_term,'translation':translation})

