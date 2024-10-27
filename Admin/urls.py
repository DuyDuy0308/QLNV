from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dangnhap, name='dangnhap'),
    path('add_taikhoan/', views.add_taikhoan, name='add_taikhoan'),
    path('list-taikhoans/', views.list_taikhoans, name='list_taikhoans'),
    path('tai-khoan/doi-mat-khau/<int:user_id>/', views.doi_mat_khau, name='doi_mat_khau'),
    path('AD', views.trangchu, name='trangchu'),
    path('themtin', views.themtin, name='themtin'),
    path('suatin/<int:pk>/', views.suatin, name='suatin'),
    path('xoatin/<int:pk>/', views.xoatin, name='xoatin'),
    path('congtyBH', views.congtyBH, name='congtyBH'),
    path('suacongtyBH/<int:pk>/', views.suacongtyBH, name='suacongtyBH'),
    path('xoacongtyBH/<int:pk>/', views.xoacongtyBH, name='xoacongtyBH'),
    path('TKH', views.themkhachhang, name='themkhachhang'),
    path('khach-hang/xoa/<int:khachhang_id>/', views.xoa_khach_hang, name='xoa_khach_hang'),
    path('khach-hang/sua/<int:khachhang_id>/', views.sua_khach_hang, name='sua_khach_hang'),
    path('khachhang/lan-gap/<int:khachhang_id>/', views.xem_lan_gap, name='xem_lan_gap'),
    path('them_lan_gap/<int:khachhang_id>/', views.them_lan_gap, name='them_lan_gap'),
    path('lan-gap/sua/<int:id>/', views.sua_lan_gap, name='sua_lan_gap'),
    path('lan-gap/xoa/<int:id>/', views.xoa_lan_gap, name='xoa_lan_gap'),
    path('KHCS', views.khachhangchamsoc, name='khachhangchamsoc'),
    path('KHSK', views.khachhangsapky, name='khachhangsapky'),
    path('KHDK', views.khachhangdaky, name='khachhangdaky'),
    path('KHLB', views.khachhangloaibo, name='khachhangloaibo'),
    path('up', views.up, name='up'),
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lesson_list_manage/', views.lesson_list_manage, name='lesson_list_manage'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lessons/<int:lesson_id>/toggle_vip/', views.toggle_vip_status, name='toggle_vip_status'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('select_receiver/', views.select_receiver, name='select_receiver'),
    path('chat/<int:receiver_id>/', views.chat_view, name='chat_view'),  # Đảm bả
# -------------------------------------------------------------------------------------
    path('up_kn', views.up_kn, name='up_kn'),
    path('lesson_list_kn/', views.lesson_list_kn, name='lesson_list_kn'),
    path('lesson_kn/<int:lesson_id>/edit/', views.edit_lesson_kn, name='edit_lesson_kn'),
    path('lesson_kn/<int:lesson_id>/delete/', views.delete_lesson_kn, name='delete_lesson_kn'),
    path('lesson_kn/<int:lesson_id>/toggle_vip/', views.toggle_vip_status_kn, name='toggle_vip_status_kn'),

    # URL for viewing lesson details
    path('lesson_kn/<int:lesson_id>/', views.lesson_detail_kn, name='lesson_detail_kn'),
# -------------------------------------------------------------------------------------
    path('trangchu_manage', views.trangchu_manage, name='trangchu_manage'),
    path('tao_doi', views.tao_doi, name='tao_doi'),
    path('list', views.list, name='list'),
    path('dangxuat', views.dangxuat, name='dangxuat'),
    path('ttnd', views.thong_tin_nguoi_dung, name='ttnd'),
    path('change-password/', views.change_password, name='change_password'),
 # -------------------------------------------------------------------------------------
    path('trangchu_user', views.trangchu_user, name='trangchu_user'),
    path('ttnd_user', views.thong_tin_nguoi_dung_user, name='ttnd_user'),
# -------------------------------------------------------------------------------------
    path('design-slide/', views.slide_design_view, name='design_slide'),
    path('save/', views.save_slides, name='save'),
    
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
