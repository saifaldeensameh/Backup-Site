from django.urls import path
from . import views

urlpatterns = [
    path('',views.newform,name='index'),
    path('upload/done/',views.done_upload,name='upload_done'),
    path('search_sku/',views.search_skus,name='search_sku'),
    path('search_batch/',views.search_ticket_batch,name='search_batch'),
    path('report/', views.report_search, name='report_search')

    # path('signup',views.signup,name='signup'),
]
