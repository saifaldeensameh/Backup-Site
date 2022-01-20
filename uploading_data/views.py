import csv
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic import UpdateView
from rest_framework import generics
from django.core.files import File

from .models import Sheet
from django.contrib.auth.decorators import login_required
from .forms import NewSheetForm,UserandSheet
from django.contrib.auth.models import User
from .models import Data_Field
from django.contrib.auth import login as auth_login
from django.utils.safestring import mark_safe

from .serializers import Data_Field_Serializer,Sheet_Serializer

import pandas as pd
from django.contrib import messages as alertmessage

#fullstack project
@login_required
def Upload(request):
    form = NewSheetForm()
    if request.method == 'POST' and 'upload_btn' in request.POST:
        form = NewSheetForm(request.POST, request.FILES)
        if form.is_valid():
            sheet = form.save(commit=False)
            submit,message = checking_found(sheet.sheeturl)
            if submit:
                # sheetsave = form.save(commit=False)
                sheet.Uploaderid = request.user
                sheet.save()
                saving_sku(sheet.sheeturl, sheet.ticketname, sheet.batchNumber)
                return redirect('upload_done')
            else:
                messages = message.split('\n')

            return render(request, 'index.html', {'form': form,'messages':messages})
    return render(request, 'index.html', {'form': form})

#checking for errors in the fullstack project
def checking_found(file):
    sku_dataframe = pd.read_csv(file)
    arr = sku_dataframe[
        ['sku', 'store_view_code', 'creatorid', 'qualityid', 'isrejected']].values.tolist()
    skufoundlist, skunanlist, creatornotfoundlist, qualitynotfoundlist, isrejectednotfoundlist = ([] for _ in range(5))
    skufound = skunan = creatornotfound = qualitynotfound = isrejectednotfound = False
    duplication_in_same_file = sku_dataframe[['sku', 'store_view_code']].duplicated().any()
    for item in range(len(arr)):
        # check the existing sku
        try:
            sku = arr[item][0]
            if str(arr[item][1]) == 'ar':
                sku += '_ar'

            get_object_or_404(Data_Field, SKU=sku)
            skufound = True
            skufoundlist.append(str(item + 2))
        except:
            if str(arr[item][0]) == 'nan':
                skunan = True
                skunanlist.append(str(item + 2))
        # check not existing creator
        try:
            get_object_or_404(User, username=arr[item][2])
            pass
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
        except:
            isrejectednotfound = True
            isrejectednotfoundlist.append(str(item + 2))

    submitbool = True
    message = ''


    if duplication_in_same_file:
        message += 'There is Duplicate in SKUs of the Sheet'
        submitbool = False

    if skunan:
        message += '\n'+'SKUs Not Found in row ' + '/'.join(skunanlist)
        submitbool = False
    if skufound:
        message += '\n'+'Duplicate SKUs in row ' + '/'.join(skufoundlist)
        submitbool = False
    if creatornotfound:
        message += '\n'+'Creatorid Not Found in row ' + '/'.join(creatornotfoundlist)
        submitbool = False
    if qualitynotfound:
        message += '\n'+'Qualityid Not Found in row ' + '/'.join(qualitynotfoundlist)
        submitbool = False
    if isrejectednotfound:
        message += '\n'+'Seif Value should be either 1 or 0 in row ' + '/'.join(isrejectednotfoundlist)
        submitbool = False

    return submitbool,message

#saving all the skus in the file
def saving_sku(file, ticketname, batchnumber):
    sku_dataframe = pd.read_csv(file)
    sku_dataframe = sku_dataframe[['sku', 'store_view_code', 'creatorid', 'qualityid', 'isrejected']].values.tolist()
    for item in sku_dataframe:
        sku = item[0]
        if str(item[1]) == 'ar':
            sku += '_ar'
        data = Data_Field()
        data.SKU = sku
        data.Creatorid = get_object_or_404(User, username=item[2])
        data.Qualityid = get_object_or_404(User, username=item[3])
        data.isRejected = item[4]
        data.Sheetid = get_object_or_404(Sheet, ticketname=ticketname, batchNumber=batchnumber)
        data.save()

#render the done upload html
def done_upload(requests):
    return render(requests, 'success_upload.html')


def search_skus(request):
    sku_data_ar = []
    sku_data = []
    if request.method == 'GET' and 'search_btn' in request.GET:
        if 'search' in request.GET:
            search_term = request.GET['search']
            search_term =search_term.split('_ar')
            search_term =search_term[0]
            sku_data = Data_Field.objects.all().filter(SKU=search_term)
            data = search_term + '_ar'
            sku_data_ar = Data_Field.objects.all().filter(SKU=data)
        data = {}
        for item in sku_data:
            print(item.Sheetid)
            sheetid = Sheet.objects.all().filter(id=item.Sheetid.id)
            sheetid = sheetid[0]
            data = {'SKU': item.SKU, "Ticket": str(sheetid.ticketname), "Batch": str(sheetid.batchNumber),
                    'Content': str(item.Creatorid), 'Rejected_Content': str(item.isRejected),
                    'Quality_Content': str(item.Qualityid),
                    'Translation': str(sku_data_ar[0].Creatorid),
                    'Rejected_Translation': str(sku_data_ar[0].isRejected),
                    'Quality_Translation': str(sku_data_ar[0].Qualityid),
                    'Majento_Name': str(sheetid.Majentoid), 'Majento_Date': str(sheetid.MajentoDate.date()),
                    'Majento_Time': str(sheetid.MajentoDate.time()),
                    'Uploader_Name': str(sheetid.Uploaderid), 'Uploaded_Date': str(sheetid.UploadedDate.date()),
                    'Uploaded_Time': str(sheetid.UploadedDate.time()), }
        # return JsonResponse(data)


        return render(request, 'Search_Sku.html', {'search': search_term, 'articles': data})
    elif request.method == 'GET' and 'export_btn' in request.GET:
        if 'search' in request.GET:
            search_term = request.GET['search']
            search_term =search_term.split('_ar')
            search_term =search_term[0]
            sku_data = Data_Field.objects.all().filter(SKU=search_term)
            data = search_term + '_ar'
            # sku_data_ar = Data_Field.objects.all().filter(SKU=data)
        data = {}
        for item in sku_data:
            # print(item.Sheetid)
            sheetid = Sheet.objects.all().filter(id=item.Sheetid.id)
            sheetid = sheetid[0]
            df = pd.read_csv(sheetid.sheeturl)
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            writer.writerow(df.columns.tolist())
            for item in df.values.tolist():
                writer.writerow(item)
            response['Content-Disposition'] = 'attachment; filename="members_sku.csv"'
            return response
        return render(request, 'Search_Sku.html',{'messages':['SKU Not Found']})

    return render(request, 'Search_Sku.html')

def search_ticket_batch(request):
    f = {}
    if request.method == 'GET' and 'search_btn' in request.GET:
        if 'search' in request.GET:
            search_term_ticket = request.GET['search']
            search_term_batch = request.GET['batch_search']
            try:
                x = int(search_term_ticket)
                x = int(search_term_batch)
            except:
                return render(request, 'Search_Ticket_Batch.html', {'search': search_term_ticket, 'batch_search': search_term_batch, 'messages': ['field is empty']})

            articles = Sheet.objects.all().filter(ticketname=search_term_ticket, batchNumber=search_term_batch)
            try:
                translation = Data_Field.objects.all().filter(Sheetid=articles[0].id).count()
            except:
                translation = 0
        for article in articles:
            majname = User.objects.all().filter(id=article.Majentoid_id)[0].username
            upname = User.objects.all().filter(id=article.Uploaderid_id)[0].username
            f = {'Ticket_Number': article.ticketname, 'Batch_Number': article.batchNumber, 'Majento_Name': majname,
                 'Majento_Date': article.MajentoDate.date(), 'Majento_Time': article.MajentoDate.time(),
                 'Uploader_Name': upname, 'Uploaded_Date': article.UploadedDate.date(),
                 'Uploaded_Time': article.UploadedDate.time(),
                 'SKU_Count': int(translation)}

        return render(request, 'Search_Ticket_Batch.html',
                          {'search': search_term_ticket, 'batch_search': search_term_batch, 'articles': f})
    elif request.method == 'GET' and 'export_btn' in request.GET:
        if 'search' in request.GET:
            search_term_ticket = request.GET['search']
            search_term_batch = request.GET['batch_search']
            try:
                articles = Sheet.objects.all().filter(ticketname=search_term_ticket, batchNumber=search_term_batch)
            except:
                pass
        for article in articles:
            df = pd.read_csv(article.sheeturl)
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            writer.writerow(df.columns.tolist())
            for item in df.values.tolist():
                writer.writerow(item)
            response['Content-Disposition'] = 'attachment; filename="members.csv"'
            return response
        return render(request, 'Search_Ticket_Batch.html',{'messages':['SKU Not Found']})


    return render(request, 'Search_Ticket_Batch.html')


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


def all_sheets(request):
    if request.method == 'GET' and 'search_btn' in request.GET:
        if 'search' in request.GET:
            search_term_ticket = request.GET['search']
            search_term_batch = request.GET['batch_search']
            try:
                x = int(search_term_ticket)
                x = int(search_term_batch)
                sheets = Sheet.objects.all().filter(ticketname=search_term_ticket, batchNumber=search_term_batch)
            except:
                sheets = []
            return render(request, 'all_sheets.html', {'sheets': sheets})
    sheets = Sheet.objects.all().order_by('-MajentoDate')
    return render(request,'all_sheets.html',{'sheets':sheets})

def all_user(request):
        x=[]

        form = UserandSheet()
        chosenusers = False
        datalist = []

        # fromdate= request.GET['from_date']
        # todate = request.GET['to_date'].
        searchfrom=''
        searchto=''
        searchname=''
        if  'from_date' not in request.GET or request.GET['from_date']=='':

            fromdate = '1900-01-01T00:00'
        else:
            fromdate = request.GET['from_date']
            searchfrom = request.GET['from_date']

        if 'to_date' not in request.GET or request.GET['to_date'] == '':
            todate = '2500-01-01T00:00'
        else:
            todate = request.GET['to_date']
            searchto = request.GET['to_date']

        if 'majento_id' in request.GET:
            form = UserandSheet(request.GET)
            # x =form.save(commit=False)
            searchname=request.GET['majento_id']
            chosenusers=True
            for i in request.GET.getlist('majento_id'):
                x .append(User.objects.all().filter(id=i))

        if chosenusers:
            users=x
        else:
            users = User.objects.all()


        for user in users:
            if chosenusers:
                user = user[0]
            creation = Data_Field.objects.all().filter(Creatorid=user,Sheetid__MajentoDate__gte=fromdate,Sheetid__MajentoDate__lte=todate).count()
            quality = Data_Field.objects.all().filter(Qualityid=user,Sheetid__MajentoDate__gte=fromdate,Sheetid__MajentoDate__lte=todate).count()
            rejection = Data_Field.objects.all().filter(Creatorid=user,Sheetid__MajentoDate__gte=fromdate,Sheetid__MajentoDate__lte=todate,isRejected=True).count()
            try:
                rejection_percentage = (rejection/quality)*100
            except:
                rejection_percentage = 0
            datalist.append( {'user':str(user),'create':str(creation),'quality':str(quality),
                                  'rejection':str(rejection),'percentage':str(rejection_percentage)})


        return render(request, 'all_users.html', {'persons': datalist,'form':form,'searchname':searchname,'searchfrom':searchfrom,'searchto':searchto})
#############################################################################
# def edit_sheet(request,sheetid):
#     sheets = get_object_or_404(Sheet, pk=sheetid)
#     print(sheets)
#     return render(request, 'edit_sheet.html', {'sheets': sheets})


class EditSheet(UpdateView):
    model = Sheet
    fields = ('sheeturl',)
    template_name = 'edit_sheet.html'
    pk_url_kwarg = 'sheetid'
    context_object_name = 'sheet'

    def form_valid(self, form):
        sheet=form.save(commit=False)
        sheet.save()
        return redirect('all_sheets')


#backend

def checking_found_api(request):
    if request.method == 'POST':
        sku_dataframe = pd.read_csv(request.FILES['sheet_url'])
        arr = sku_dataframe[
            ['sku', 'store_view_code', 'creatorid', 'qualityid', 'isrejected']].values.tolist()
        skufoundlist, skunanlist, creatornotfoundlist, qualitynotfoundlist, isrejectednotfoundlist = ([] for _ in range(5))
        skufound = skunan = creatornotfound = qualitynotfound = isrejectednotfound = False
        # print(arr)
        duplication_in_same_file = sku_dataframe[['sku', 'store_view_code']].duplicated().any()
        # duplicate = df[df.duplicated(, keep='first')]

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




        if duplication_in_same_file:
            message += 'There is Duplicate in SKUs of the Sheet'
            submitbool = False

        if skunan:
            message += '\n'+'SKUs Not Found in row ' + '/'.join(skunanlist)
            submitbool = False
        if skufound:
            message += '\n'+'Duplicate SKUs in row ' + '/'.join(skufoundlist)
            submitbool = False
        if creatornotfound:
            message += '\n'+'Creatorid Not Found in row ' + '/'.join(creatornotfoundlist)
            submitbool = False
        if qualitynotfound:
            message += '\n'+'Qualityid Not Found in row ' + '/'.join(qualitynotfoundlist)
            submitbool = False
        if isrejectednotfound:
            message += '\n'+'Seif Value should be either 1 or 0 in row ' + '/'.join(isrejectednotfoundlist)
            submitbool = False

        return JsonResponse({'submitbool':submitbool,'message':message})


def search_skus_api(request):
    sku_data_ar = []
    sku_data=[]
    if 'search' in request.GET:
        search_term = request.GET['search']
        search_term = search_term.split('_ar')
        search_term = search_term[0]
        sku_data = Data_Field.objects.all().filter(SKU=search_term)
        data = search_term+'_ar'
        sku_data_ar = Data_Field.objects.all().filter(SKU=data)
    data ={}
    for item in sku_data:
        print(item.Sheetid)
        sheetid = Sheet.objects.all().filter(id=item.Sheetid.id)
        sheetid = sheetid[0]
        data = {'SKU': item.SKU,"Ticket":str(sheetid.ticketname),"Batch":str(sheetid.batchNumber),
                'Content':str(item.Creatorid),'Rejected_Content':str(item.isRejected),'Quality_Content':str(item.Qualityid),
                'Translation':str(sku_data_ar[0].Creatorid),'Rejected_Translation':str(sku_data_ar[0].isRejected),'Quality_Translation':str(sku_data_ar[0].Qualityid),
                'Majento_Name': str(sheetid.Majentoid),'Majento_Date': str(sheetid.MajentoDate.date()),'Majento_Time': str(sheetid.MajentoDate.time()),
          'Uploader_Name': str(sheetid.Uploaderid),'Uploaded_Date': str(sheetid.UploadedDate.date()),'Uploaded_Time': str(sheetid.UploadedDate.time()),}
    return JsonResponse(data)


def search_ticket_batch_api(request):
    articles =[]

    if 'search' in request.GET:
        search_term_ticket = request.GET['search']
        search_term_batch = request.GET['batch_search']
        try:
            articles = Sheet.objects.all().filter(ticketname=search_term_ticket,batchNumber=search_term_batch)
        except:
            pass

        try:
            translation = Data_Field.objects.all().filter(Sheetid=articles[0].id).count()
        except:
            translation=0
      # return render(request, 'Search_Ticket_Batch.html', {'articles': articles, 'search_term': search_term_ticket, 'translation': translation})
    f= {}
    df=''
    for article in articles:
        majname = User.objects.all().filter(id=article.Majentoid_id)[0].username
        upname = User.objects.all().filter(id=article.Uploaderid_id)[0].username
        f={'Ticket_Number':article.ticketname,'Batch_Number':article.batchNumber,'Majento_Name':majname,
           'Majento_Date':article.MajentoDate.date(),'Majento_Time':article.MajentoDate.time(),'Uploader_Name':upname,'Uploaded_Date':article.UploadedDate.date(),'Uploaded_Time':article.UploadedDate.time(),
           'SKU_Count': int(translation)}
    return JsonResponse(f)

def export_csv_batch_api(request):
    articles =[]
    if 'search' in request.GET:
        search_term_ticket = request.GET['search']
        search_term_batch = request.GET['batch_search']
        try:
            articles = Sheet.objects.all().filter(ticketname=search_term_ticket,batchNumber=search_term_batch)
        except:
            pass
    for article in articles:
        df = pd.read_csv(article.sheeturl)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(df.columns.tolist())
        for item in df.values.tolist():
            writer.writerow(item)
        response['Content-Disposition'] = 'attachment; filename="members.csv"'
        return response
    return JsonResponse({'Not Found':'Sorry'})


def export_csv_sku_api(request):
    sku_data =[]
    if 'search' in request.GET:
        search_term = request.GET['search']
        search_term = search_term.split('_ar')
        search_term = search_term[0]
        sku_data = Data_Field.objects.all().filter(SKU=search_term)
        data = search_term + '_ar'
        sku_data_ar = Data_Field.objects.all().filter(SKU=data)
        # return render(request, 'Search_Sku.html', {'articles': articles, 'search_term': search_term,'translation':translation})

    data = {}
    for item in sku_data:
        # print(item.Sheetid)
        sheetid = Sheet.objects.all().filter(id=item.Sheetid.id)
        sheetid = sheetid[0]
        df = pd.read_csv(sheetid.sheeturl)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(df.columns.tolist())
        for item in df.values.tolist():
            writer.writerow(item)
        response['Content-Disposition'] = 'attachment; filename="members_sku.csv"'
        return response
    return JsonResponse({'Not Found':'Sorry'})

class Upload_Sheet_api(generics.CreateAPIView):
    queryset = Sheet.objects.all()
    serializer_class = Sheet_Serializer

class Edit_Sheet_api(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sheet.objects.all()
    serializer_class = Sheet_Serializer
    lookup_field = "id"


class Upload_SKU_api(generics.CreateAPIView):
    queryset = Data_Field.objects.all()
    serializer_class = Data_Field_Serializer



class Edit_SKU_api(generics.RetrieveUpdateDestroyAPIView):
    queryset = Data_Field.objects.all()
    serializer_class = Data_Field_Serializer
    lookup_field = 'SKU'
    # lookup_field = 'id'
