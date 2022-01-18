from django.urls import path
from . import views

urlpatterns = [
    path('',views.Upload,name='index'),
    path('upload/done/',views.done_upload,name='upload_done'),
    path('search_sku/',views.search_skus,name='search_sku'),
    path('search_batch/',views.search_ticket_batch,name='search_batch'),
    path('report/', views.report_search, name='report_search'),

    path('upload_api/', views.Upload_api.as_view(), name='index'),
    path('search_sku_api/', views.search_skus_api, name='search_sku'),
    path('search_batch_api/', views.search_ticket_batch_api, name='search_batch'),

    # path('signup',views.signup,name='signup'),
]
