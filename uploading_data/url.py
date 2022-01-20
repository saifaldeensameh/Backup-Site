from django.urls import path
from . import views

urlpatterns = [
    path('',views.Upload,name='index'),
    path('upload/done/',views.done_upload,name='upload_done'),
    path('search_sku/',views.search_skus,name='search_sku'),
    path('search_batch/',views.search_ticket_batch,name='search_batch'),
    # path('report/', views.report_search, name='report_search'),
    path('edit/',views.all_sheets,name='all_sheets'),
    path('edit/<int:sheetid>/',views.EditSheet.as_view(),name='edit_sheet'),
    path('report/', views.all_user, name='all_users'),


    path('search_sku_api/', views.search_skus_api, name='search_sku_api'),
    path('search_batch_api/', views.search_ticket_batch_api, name='search_batch_api'),
    path('upload_sheet_api/', views.Upload_Sheet_api.as_view(), name='upload_sheet_api'),
    path('upload_sku_api/', views.Upload_SKU_api.as_view(), name='upload_sku_api'),
    path('edit_sheet_api/<int:id>/',views.Edit_Sheet_api.as_view(), name='edit_sheet_api'),
    path('edit_sku_api/<slug:SKU>/',views.Edit_SKU_api.as_view(), name='edit_sku_api'),
    path('upload_api/', views.Upload_api.as_view(), name='index'),
    path('search_sku_api/', views.search_skus_api, name='search_sku'),
    path('search_batch_api/', views.search_ticket_batch_api, name='search_batch'),

    # path('signup',views.signup,name='signup'),
]



