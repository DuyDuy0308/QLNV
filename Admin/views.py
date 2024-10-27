from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import News, Taikhoan, Congtybaohiem, Danhgia, Khachhang, Lesson, Doi, LanGap, Lesson_KN, Slide, Message
from .forms import NewsForm, LessonUploadForm, LessonUploadForm_KN, TaikhoanForm
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
import json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def dangnhap(request):
    if request.method == 'POST':
        tai_khoan = request.POST['username']
        mat_khau = request.POST['password']
        
        try:
            # Tìm kiếm tài khoản trong cơ sở dữ liệu
            user = Taikhoan.objects.get(tai_khoan=tai_khoan)
            
            # Kiểm tra mật khẩu bằng cách so sánh với mật khẩu mã hóa trong cơ sở dữ liệu
            if check_password(mat_khau, user.mat_khau):
                # Lưu id của tài khoản vào session
                request.session['taikhoan_id'] = user.id

                # Kiểm tra xem tài khoản này có phải của khách hàng VIP không
                if user.khachhang and user.khachhang.IS_VIP:
                    request.session['is_vip'] = True
                else:
                    request.session['is_vip'] = False

                # Kiểm tra phân quyền
                if user.phan_quyen == 'admin':
                    return redirect('trangchu') 
                elif user.phan_quyen == 'manage':
                    return redirect('trangchu_manage') 
                else:
                    return redirect('trangchu_user')  
            else:
                return render(request, 'dangnhap.html', {'error': 'Mật khẩu không chính xác.'})

        except Taikhoan.DoesNotExist:
            return render(request, 'dangnhap.html', {'error': 'Tài khoản không tồn tại.'})
    
    return render(request, 'dangnhap.html')

def add_taikhoan(request):
    if request.method == 'POST':
        form = TaikhoanForm(request.POST)
        if form.is_valid():
            taikhoan = form.save(commit=False)
            # Hash the password before saving
            taikhoan.mat_khau = make_password(form.cleaned_data['mat_khau'])
            taikhoan.save()  # Save the new account with hashed password
            messages.success(request, 'Tài khoản đã được thêm thành công!')
            return redirect('add_taikhoan')
    else:
        form = TaikhoanForm()

    return render(request, 'add_taikhoan.html', {'form': form})

def list_taikhoans(request):
    accounts = Taikhoan.objects.select_related('khachhang').all()
    return render(request, 'list_tk.html', {'accounts': accounts})
    

def doi_mat_khau(request, user_id):
    taikhoan = get_object_or_404(Taikhoan, id=user_id)

    if request.method == 'POST':
        mat_khau_moi = request.POST['mat_khau']

        # Mã hóa mật khẩu mới
        mat_khau_moi_ma_hoa = make_password(mat_khau_moi)

        # Cập nhật mật khẩu đã mã hóa
        taikhoan.mat_khau = mat_khau_moi_ma_hoa
        taikhoan.save()

        return redirect('list_taikhoans')  # Quay về trang danh sách tài khoản

    return render(request, 'doi_mat_khau.html', {'taikhoan': taikhoan})

def dangxuat(request):
    try:
        del request.session['tai_khoan']  # Xóa tài khoản khỏi session
    except KeyError:
        pass
    return redirect('dangnhap')

def trangchu(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('trangchu')
    else:
        form = NewsForm()

    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'trangchu.html', {'form': form, 'news_list': news_list})

def themtin(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        title = request.POST.get('title')
        content = request.POST.get('content')
        media = request.FILES.get('media')  # Nhận file ảnh hoặc video

        # Lưu vào database
        news = News(title=title, content=content, media=media)
        news.save()
        messages.success(request, 'Tin tức đã được thêm thành công!')

        return redirect('trangchu')

    # Hiển thị danh sách tin tức
    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'themtin.html', {'news_list': news_list})

def suatin(request, pk):
    news = get_object_or_404(News, pk=pk)  # Lấy tin tức theo pk
    
    if request.method == "POST":
        # Lấy dữ liệu từ form HTML
        title = request.POST.get('title')
        content = request.POST.get('content')

        # Cập nhật tiêu đề và nội dung
        news.title = title
        news.content = content
        
        # Kiểm tra và xử lý file (nếu có)
        if request.FILES.get('media'):
            media = request.FILES['media']
            news.media = media  # Cập nhật file media
        try:
            news.save()  # Cố gắng lưu
            messages.success(request, 'Tin tức đã được cập nhật thành công!')
            return redirect('trangchu')  # Chuyển hướng sau khi lưu thành công
        except Exception as e:  # Bắt mọi ngoại lệ
            messages.error(request, 'Tin tức đã được cập nhật thất bại!')
            return redirect('trangchu')
    
    # Truyền dữ liệu tin tức vào template để hiển thị trong form
    return render(request, 'suatin.html', {'news': news})

def xoatin(request, pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()  # Xóa tin tức
    messages.error(request, 'Tin tức đã được xóa thành công!')
    return redirect('trangchu')  # Redirect về trang danh sách tin tức sau khi xóa

def congtyBH(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        Ten_cong_ty = request.POST.get('tencongtyBH')

        # Lưu vào database
        news = Congtybaohiem(Ten_cong_ty=Ten_cong_ty)
        news.save()
        messages.success(request, 'công ty đã được thêm thành công!')

        return redirect('congtyBH')

    # Hiển thị danh sách tin tức
    congtyBH = Congtybaohiem.objects.all()
    return render(request, 'congtyBH.html', {'congtyBH': congtyBH})

def suacongtyBH(request, pk):
    pkbh = get_object_or_404(Congtybaohiem, pk=pk)  # Lấy tin tức theo pk
    
    if request.method == "POST":
        # Lấy dữ liệu từ form HTML
        tencongtynew = request.POST.get('tencongtynew')

        # Cập nhật tiêu đề và nội dung
        pkbh.Ten_cong_ty = tencongtynew

        pkbh.save()  # Cố gắng lưu
        messages.success(request, 'Công ty bảo hiểmđã được cập nhật thành công!')
        return redirect('congtyBH')  # Chuyển hướng sau khi lưu thành công
       
    # Truyền dữ liệu tin tức vào template để hiển thị trong form
    return render(request, 'suabh.html', {'pkbhs': pkbh})

def xoacongtyBH(request, pk):
    pkbh = get_object_or_404(Congtybaohiem, pk=pk)
    pkbh.delete()  # Xóa tin tức
    messages.error(request, 'Công ty bảo hiểm đã được xóa thành công!')
    return redirect('congtyBH')  # Redirect về trang danh sách tin tức sau khi xóa

def themkhachhang(request):
    if request.method == 'POST':
        ho_va_ten = request.POST.get('ho_va_ten')
        ngay_sinh = request.POST.get('ngay_sinh')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        dia_chi = request.POST.get('dia_chi')
        cong_ty_ids = request.POST.getlist('cong_ty_bao_hiem')  # Lấy danh sách công ty
        tham_gia_bao_hiem = request.POST.get('tham_gia_bao_hiem') == 'option1'
        chi_tiet_bao_hiem = request.POST.get('chi_tiet_bao_hiem')
        danh_gia = request.POST.get('danh_gia')
        is_vip = request.POST.get('is_vip') == 'on'  # Lấy giá trị VIP từ form
        
        # Tạo đối tượng khách hàng mới
        khach_hang = Khachhang(
            ho_va_ten=ho_va_ten,
            ngay_sinh=ngay_sinh,
            so_dien_thoai=so_dien_thoai,
            dia_chi=dia_chi,
            tham_gia_bao_hiem=tham_gia_bao_hiem,
            chi_tiet_bao_hiem=chi_tiet_bao_hiem,
            danh_gia=Danhgia.objects.get(id=danh_gia),
            IS_VIP=is_vip  # Lưu giá trị VIP
        )
        khach_hang.save()

        # Lưu các công ty bảo hiểm
        for cong_ty_id in cong_ty_ids:
            cong_ty = Congtybaohiem.objects.get(id=cong_ty_id)
            khach_hang.cong_ty_bao_hiem.add(cong_ty)

        # Lưu các lần gặp
        lan_gap_list = request.POST.getlist('lan_gap')  # Lấy danh sách các lần gặp từ form
        for lan_gap in lan_gap_list:
            if lan_gap:  # Chỉ lưu nếu nội dung không rỗng
                LanGap.objects.create(
                    khach_hang=khach_hang,
                    noi_dung=lan_gap,
                )

        return redirect('themkhachhang')  # Điều hướng đến trang thông báo thành công

    # Lấy dữ liệu cho form
    cong_ty_bao_hiem_list = Congtybaohiem.objects.all()
    danh_gia_list = Danhgia.objects.all()

    return render(request, 'tkh.html', {
        'cong_ty_bao_hiem_list': cong_ty_bao_hiem_list,
        'danh_gia_list': danh_gia_list
    })


def xoa_khach_hang(request, khachhang_id):
    # Kiểm tra phương thức là POST
    if request.method == 'POST':
        khachhang = get_object_or_404(Khachhang, id=khachhang_id)
        khachhang.delete()  # Xóa khách hàng
        return redirect('trangchu')  # Redirect đến danh sách khách hàng

    return redirect('trangchu')

def sua_khach_hang(request, khachhang_id):
    khachhang = get_object_or_404(Khachhang, id=khachhang_id)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        ho_va_ten = request.POST.get('ho_va_ten')
        ngay_sinh = request.POST.get('ngay_sinh')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        dia_chi = request.POST.get('dia_chi')
        cong_ty_ids = request.POST.getlist('cong_ty_bao_hiem')  # Lấy danh sách công ty
        tham_gia_bao_hiem = request.POST.get('tham_gia_bao_hiem') == 'option1'
        chi_tiet_bao_hiem = request.POST.get('chi_tiet_bao_hiem')
        danh_gia = request.POST.get('danh_gia')
        is_vip = request.POST.get('is_vip') == 'on'  # Lấy giá trị VIP từ form

        # Cập nhật thông tin khách hàng
        khachhang.ho_va_ten = ho_va_ten
        khachhang.ngay_sinh = ngay_sinh
        khachhang.so_dien_thoai = so_dien_thoai
        khachhang.dia_chi = dia_chi
        khachhang.tham_gia_bao_hiem = tham_gia_bao_hiem
        khachhang.chi_tiet_bao_hiem = chi_tiet_bao_hiem
        khachhang.danh_gia = Danhgia.objects.get(id=danh_gia)
        khachhang.IS_VIP = is_vip
        khachhang.save()

        # Cập nhật các công ty bảo hiểm
        khachhang.cong_ty_bao_hiem.set(cong_ty_ids)

        return redirect('trangchu')  # Điều hướng về danh sách khách hàng sau khi lưu

    # Lấy dữ liệu cho form
    cong_ty_bao_hiem_list = Congtybaohiem.objects.all()
    danh_gia_list = Danhgia.objects.all()

    return render(request, 'sua_khach_hang.html', {
        'khachhang': khachhang,
        'cong_ty_bao_hiem_list': cong_ty_bao_hiem_list,
        'danh_gia_list': danh_gia_list
    })
def xem_lan_gap(request, khachhang_id):
    khachhang = get_object_or_404(Khachhang, id=khachhang_id)
    # Giả sử bạn có một model tên là LanGap chứa thông tin về các lần gặp
    lan_gap_list = LanGap.objects.filter(khach_hang=khachhang)

    return render(request, 'xem.html', {
        'khachhang': khachhang,
        'lan_gap_list': lan_gap_list
    })
def them_lan_gap(request, khachhang_id):
    if request.method == 'POST':
        khachhang = get_object_or_404(Khachhang, id=khachhang_id)
        lan_gap_list = request.POST.getlist('lan_gap')  # Lấy tất cả ghi chú từ form
        for noi_dung in lan_gap_list:
            if noi_dung:  # Kiểm tra nếu ghi chú không rỗng
                LanGap.objects.create(khach_hang=khachhang, noi_dung=noi_dung)
        return redirect('xem_lan_gap', khachhang_id=khachhang.id)  # Điều hướng lại tới trang xem

def sua_lan_gap(request, id):
    lan_gap = get_object_or_404(LanGap, id=id)
    if request.method == 'POST':
        lan_gap.noi_dung = request.POST.get('noi_dung')
        lan_gap.save()
        return redirect('xem_lan_gap', khachhang_id=lan_gap.khach_hang.id)  # Điều hướng lại tới trang xem
    return render(request, 'sua_lan_gap.html', {'lan_gap': lan_gap})
def xoa_lan_gap(request, id):
    lan_gap = get_object_or_404(LanGap, id=id)
    khach_hang_id = lan_gap.khach_hang.id  # Lưu id khách hàng trước khi xóa
    lan_gap.delete()
    return redirect('xem_lan_gap', khachhang_id=khach_hang_id)  # Điều hướng lại tới trang xem

def khachhangchamsoc(request):
    khachhangs = Khachhang.objects.filter(danh_gia__Loai_KH='Khách hàng chăm sóc')
    context = {
        'khachhangs': khachhangs,
    }
    return render(request, 'khcs.html', context)

def khachhangsapky(request):
    khachhangs = Khachhang.objects.filter(danh_gia__Loai_KH='Khách hàng sắp ký')
    context = {
        'khachhangs': khachhangs,
    }
    return render(request, 'khsk.html', context)

def khachhangdaky(request):
    khachhangs = Khachhang.objects.filter(danh_gia__Loai_KH='Khách hàng đã ký')
    context = {
        'khachhangs': khachhangs,
    }
    return render(request, 'khdk.html', context)

def khachhangloaibo(request):
    khachhangs = Khachhang.objects.filter(danh_gia__Loai_KH='Khách hàng loại bỏ')
    context = {
        'khachhangs': khachhangs,
    }
    return render(request, 'khlb.html', context)

def lesson_list(request):
    # Lấy thông tin tài khoản từ session
    taikhoan_id = request.session.get('taikhoan_id')

    if not taikhoan_id:
        # Nếu không có thông tin tài khoản trong session, yêu cầu đăng nhập lại
        return HttpResponseForbidden("Bạn chưa đăng nhập. Vui lòng đăng nhập để xem nội dung.")

    # Lấy tài khoản từ cơ sở dữ liệu
    taikhoan = get_object_or_404(Taikhoan, id=taikhoan_id)

    # Lấy trạng thái VIP từ session
    is_vip = request.session.get('is_vip', False)  # Mặc định là False nếu không có giá trị trong session

    # Kiểm tra phân quyền của tài khoản và trạng thái VIP
    if taikhoan.phan_quyen == 'admin':
        # Nếu là admin, xem tất cả bài học
        lessons = Lesson.objects.all()
    elif is_vip:
        # Nếu là VIP, xem tất cả bài học, kể cả VIP-only
        lessons = Lesson.objects.all()
    else:
        # Nếu không phải VIP, chỉ xem bài học không phải VIP
        lessons = Lesson.objects.filter(vip_only=False)

    return render(request, 'kienthuc.html', {'lessons': lessons, 'taikhoan': taikhoan})

def lesson_list_manage(request):
    # Lấy thông tin tài khoản từ session
    taikhoan_id = request.session.get('taikhoan_id')

    if not taikhoan_id:
        # Nếu không có thông tin tài khoản trong session, yêu cầu đăng nhập lại
        return HttpResponseForbidden("Bạn chưa đăng nhập. Vui lòng đăng nhập để xem nội dung.")

    # Lấy tài khoản từ cơ sở dữ liệu
    taikhoan = get_object_or_404(Taikhoan, id=taikhoan_id)

    # Lấy trạng thái VIP từ session
    is_vip = request.session.get('is_vip', False)  # Mặc định là False nếu không có giá trị trong session

    # Kiểm tra phân quyền của tài khoản và trạng thái VIP
    if taikhoan.phan_quyen == 'admin':
        # Nếu là admin, xem tất cả bài học
        lessons = Lesson.objects.all()
    elif is_vip:
        # Nếu là VIP, xem tất cả bài học, kể cả VIP-only
        lessons = Lesson.objects.all()
    else:
        # Nếu không phải VIP, chỉ xem bài học không phải VIP
        lessons = Lesson.objects.filter(vip_only=False)

    return render(request, 'kienthuc_manage.html', {'lessons': lessons, 'taikhoan': taikhoan})

def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        # Manually handling form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        vip_only = request.POST.get('vip_only') == 'on'  # Checkbox handling

        # Update lesson with new data
        lesson.title = title
        lesson.description = description
        lesson.vip_only = vip_only

        # Handle file updates if provided
        if request.FILES.get('video'):
            lesson.video = request.FILES['video']
        if request.FILES.get('image'):
            lesson.image = request.FILES['image']
        if request.FILES.get('ppt'):
            lesson.ppt = request.FILES['ppt']

        lesson.save()  # Save changes # Redirect to lesson detail page
        return redirect('lesson_list')
    return render(request, 'edit_lesson.html', {'lesson': lesson})

def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Bài học đã được xóa thành công!')
        return redirect('lesson_list')  # Redirect to the lesson list or another appropriate view

    return render(request, 'confirm_delete.html', {'lesson': lesson})

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    ppt_url = None
    if lesson.ppt:
        ppt_url = request.build_absolute_uri(lesson.ppt.url)  # Tạo URL đầy đủ cho PPT

    return render(request, 'phat.html', {
        'lesson': lesson,
        'ppt_url': ppt_url  # Truyền URL của PPT vào template
    })


def up(request):
    if request.method == 'POST':
        form = LessonUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Lưu bài học vào cơ sở dữ liệu
            return redirect('lesson_list')  # Chuyển hướng đến danh sách bài học
    else:
        form = LessonUploadForm()

    return render(request, 'up.html', {'form': form})

def toggle_vip_status(request, lesson_id):
    # Lấy id của người dùng từ session
    taikhoan_id = request.session.get('taikhoan_id')
    
    if not taikhoan_id:
        return HttpResponseForbidden("Bạn chưa đăng nhập. Vui lòng đăng nhập để thực hiện thao tác này.")
    
    # Lấy tài khoản từ cơ sở dữ liệu
    taikhoan = get_object_or_404(Taikhoan, id=taikhoan_id)

    # Kiểm tra phân quyền
    if taikhoan.phan_quyen != 'admin':
        return HttpResponseForbidden("Bạn không có quyền thay đổi trạng thái này.")

    # Tìm bài học theo ID
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Thay đổi trạng thái VIP
    lesson.vip_only = not lesson.vip_only
    lesson.save()

    # Quay về trang danh sách bài học sau khi thay đổi
    return redirect('lesson_list')

# ------------------------------------
def lesson_list_kn(request):
    # Lấy thông tin tài khoản từ session
    taikhoan_id = request.session.get('taikhoan_id')

    if not taikhoan_id:
        # Nếu không có thông tin tài khoản trong session, yêu cầu đăng nhập lại
        return HttpResponseForbidden("Bạn chưa đăng nhập. Vui lòng đăng nhập để xem nội dung.")

    # Lấy tài khoản từ cơ sở dữ liệu
    taikhoan = get_object_or_404(Taikhoan, id=taikhoan_id)

    # Lấy trạng thái VIP từ session
    is_vip = request.session.get('is_vip', False)  # Mặc định là False nếu không có giá trị trong session

    # Kiểm tra phân quyền của tài khoản và trạng thái VIP
    if taikhoan.phan_quyen == 'admin':
        # Nếu là admin, xem tất cả bài học
        lessons = Lesson_KN.objects.all()
    elif is_vip:
        # Nếu là VIP, xem tất cả bài học, kể cả VIP-only
        lessons = Lesson_KN.objects.all()
    else:
        # Nếu không phải VIP, chỉ xem bài học không phải VIP
        lessons = Lesson_KN.objects.filter(vip_only=False)

    return render(request, 'kynang.html', {'lessons': lessons, 'taikhoan': taikhoan})

def edit_lesson_kn(request, lesson_id):
    lesson = get_object_or_404(Lesson_KN, id=lesson_id)

    if request.method == 'POST':
        # Manually handling form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        vip_only = request.POST.get('vip_only') == 'on'  # Checkbox handling

        # Update lesson with new data
        lesson.title = title
        lesson.description = description
        lesson.vip_only = vip_only

        # Handle file updates if provided
        if request.FILES.get('video'):
            lesson.video = request.FILES['video']
        if request.FILES.get('image'):
            lesson.image = request.FILES['image']
        if request.FILES.get('ppt'):
            lesson.ppt = request.FILES['ppt']

        lesson.save()  # Save changes # Redirect to lesson detail page
        return redirect('lesson_list_kn')
    return render(request, 'edit_lesson_kn.html', {'lesson': lesson})

def delete_lesson_kn(request, lesson_id):
    lesson = get_object_or_404(Lesson_KN, id=lesson_id)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Bài học đã được xóa thành công!')
        return redirect('lesson_list_kn')  # Redirect to the lesson list or another appropriate view

    return render(request, 'confirm_delete.html', {'lesson': lesson})

def lesson_detail_kn(request, lesson_id):
    lesson = get_object_or_404(Lesson_KN, id=lesson_id)
    
    ppt_url = None
    if lesson.ppt:
        ppt_url = request.build_absolute_uri(lesson.ppt.url)  # Tạo URL đầy đủ cho PPT

    return render(request, 'phat.html', {
        'lesson': lesson,
        'ppt_url': ppt_url  # Truyền URL của PPT vào template
    })


def up_kn(request):
    if request.method == 'POST':
        form = LessonUploadForm_KN(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Lưu bài học vào cơ sở dữ liệu
            return redirect('lesson_list_kn')  # Chuyển hướng đến danh sách bài học
    else:
        form = LessonUploadForm_KN()

    return render(request, 'up_KN.html', {'form': form})

def toggle_vip_status_kn(request, lesson_id):
    # Lấy id của người dùng từ session
    taikhoan_id = request.session.get('taikhoan_id')
    
    if not taikhoan_id:
        return HttpResponseForbidden("Bạn chưa đăng nhập. Vui lòng đăng nhập để thực hiện thao tác này.")
    
    # Lấy tài khoản từ cơ sở dữ liệu
    taikhoan = get_object_or_404(Taikhoan, id=taikhoan_id)

    # Kiểm tra phân quyền
    if taikhoan.phan_quyen != 'admin':
        return HttpResponseForbidden("Bạn không có quyền thay đổi trạng thái này.")

    # Tìm bài học theo ID
    lesson = get_object_or_404(Lesson_KN, id=lesson_id)

    # Thay đổi trạng thái VIP
    lesson.vip_only = not lesson.vip_only
    lesson.save()

    # Quay về trang danh sách bài học sau khi thay đổi
    return redirect('lesson_list_kn')
# ------------------------------------
def trangchu_manage(request):
    news_list = News.objects.all()
    return render(request, 'trangchu_manage.html', {'news_list': news_list})


def trangchu_user(request):
    news_list = News.objects.all()
    return render(request, 'trangchu_user.html', {'news_list': news_list})

def tao_doi(request):
    if request.method == 'POST':
        so_dien_thoai = request.POST.get('so_dien_thoai')

        try:
            # Tìm khách hàng theo số điện thoại
            khachhang = Khachhang.objects.get(so_dien_thoai=so_dien_thoai)

            # Lấy quản lý hiện tại từ session
            quan_ly_id = request.session.get('taikhoan_id')
            quan_ly = Taikhoan.objects.get(id=quan_ly_id)

            # Kiểm tra xem quản lý đã có đội hay chưa
            doi, created = Doi.objects.get_or_create(quan_ly=quan_ly)

            # Cập nhật đội cho khách hàng
            khachhang.doi = doi
            khachhang.quan_ly = quan_ly  # Gán quản lý là tài khoản hiện tại
            khachhang.save()

            if created:
                messages.success(request, f"Đội đã được tạo cho quản lý {quan_ly.tai_khoan} và khách hàng {khachhang.ho_va_ten} đã được thêm vào đội.")
            else:
                messages.success(request, f"Khách hàng {khachhang.ho_va_ten} đã được thêm vào đội của quản lý {quan_ly.tai_khoan}.")

        except Khachhang.DoesNotExist:
            messages.error(request, "Không tìm thấy khách hàng với số điện thoại này.")
        except Taikhoan.DoesNotExist:
            messages.error(request, "Quản lý không tồn tại.")
        
        return redirect('trangchu_manage') 

    return render(request, 'tao_doi.html')

def list(request):
    quan_ly_id = request.session.get('taikhoan_id')

    try:
        # Lấy quản lý hiện tại
        quan_ly = Taikhoan.objects.get(id=quan_ly_id)

        # Lấy đội của quản lý
        doi = Doi.objects.get(quan_ly=quan_ly)

        # Lấy danh sách khách hàng trong đội
        khach_hang_list = Khachhang.objects.filter(doi=doi)

        return render(request, 'list.html', {'khach_hang_list': khach_hang_list, 'doi': doi})

    except Taikhoan.DoesNotExist:
        messages.error(request, "Quản lý không tồn tại.")
        return redirect('trangchu_manage')
    except Doi.DoesNotExist:
        messages.warning(request, "Quản lý này chưa có đội.")
        return render(request, 'list.html', {'khach_hang_list': [], 'doi': None})

def thong_tin_nguoi_dung(request):
    if 'taikhoan_id' in request.session:
        taikhoan_id = request.session['taikhoan_id']
        
        try:
            taikhoan = Taikhoan.objects.get(id=taikhoan_id)
            khachhang = Khachhang.objects.filter(taikhoan=taikhoan).first()

            if request.method == 'POST':
                # Thay đổi trạng thái VIP
                if khachhang:
                    khachhang.IS_VIP = not khachhang.IS_VIP
                    khachhang.save()
                    return redirect('ttnd')  # Reload trang sau khi thay đổi

            context = {
                'taikhoan': taikhoan,
                'khachhang': khachhang
            }

            return render(request, 'thong_tin_nguoi_dung.html', context)

        except Taikhoan.DoesNotExist:
            return render(request, 'error.html', {'message': 'Tài khoản không tồn tại.'})
    else:
        return render(request, 'error.html', {'message': 'Người dùng chưa đăng nhập.'})
    
def change_password(request):
    if 'taikhoan_id' in request.session:
        taikhoan_id = request.session['taikhoan_id']

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = Taikhoan.objects.get(id=taikhoan_id)

        # Kiểm tra mật khẩu hiện tại (sử dụng check_password)
        if not check_password(current_password, user.mat_khau):
            return HttpResponse("Mật khẩu hiện tại không đúng.")

        # Kiểm tra xem mật khẩu mới và xác nhận mật khẩu có khớp không
        if new_password != confirm_password:
            return HttpResponse("Mật khẩu mới không khớp.")

        # Cập nhật mật khẩu mới (sử dụng set_password)
        user.mat_khau = make_password(new_password)
        user.save()
        return HttpResponse("Mật khẩu đã được thay đổi thành công.")

    return render(request, 'change_password.html')


from django.views.decorators.csrf import csrf_exempt

def slide_design_view(request):
    return render(request, 'slide.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .models import Slide
import os
from django.template.loader import render_to_string

def save_slides(request):
    if request.method == 'POST':
        try:
            # Đọc dữ liệu JSON từ request
            data = json.loads(request.body)
            file_name = data.get('file_name')
            slides = data.get('slides')

            if not file_name or not slides:
                return JsonResponse({'message': 'Thiếu tên file hoặc slide'}, status=400)

        # Tạo một phiên làm việc mới trong SlideSession
            slide_session = Slide.objects.create(name=file_name)

        # Xác định đường dẫn lưu file HTML
            file_path = os.path.join(settings.MEDIA_ROOT, f'{file_name}.html')

        # Tạo nội dung HTML từ các slide
            html_content = render_to_string('slides_template.html', {'slides': slides})

        # Ghi nội dung vào file HTML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        # Lưu URL file trong model
            slide_session.file_url = os.path.join(settings.MEDIA_URL, f'{file_name}.html')
            slide_session.save()

            return JsonResponse({'message': f'Slides đã được lưu với tên: {file_name}'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Chỉ chấp nhận yêu cầu POST'}, status=405)
    
def select_receiver(request):
    # Lấy tất cả tài khoản mà người dùng có thể nhắn tin đến
    users = Taikhoan.objects.all().exclude(id=request.session.get('taikhoan_id'))  # Trừ tài khoản của chính người dùng
    return render(request, 'select_receiver.html', {'users': users})


def chat_view(request, receiver_id):
    receiver = Taikhoan.objects.get(id=receiver_id)
    messages = Message.objects.filter(
        sender__in=[request.session['taikhoan_id'], receiver_id],
        receiver__in=[request.session['taikhoan_id'], receiver_id]
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        # Lưu tin nhắn mà không có thông báo
        Message.objects.create(sender_id=request.session['taikhoan_id'], receiver=receiver, content=content)
        return redirect('chat_view', receiver_id=receiver_id)  # Quay lại trang chat mà không thông báo

    return render(request, 'chat_admin.html', {'receiver': receiver, 'messages': messages})

def thong_tin_nguoi_dung_user(request):
    if 'taikhoan_id' in request.session:
        taikhoan_id = request.session['taikhoan_id']
        
        try:
            taikhoan = Taikhoan.objects.get(id=taikhoan_id)
            khachhang = Khachhang.objects.filter(taikhoan=taikhoan).first()

            if request.method == 'POST':
                # Thay đổi trạng thái VIP
                if khachhang:
                    khachhang.IS_VIP = not khachhang.IS_VIP
                    khachhang.save()
                    return redirect('ttnd')  # Reload trang sau khi thay đổi

            context = {
                'taikhoan': taikhoan,
                'khachhang': khachhang
            }

            return render(request, 'ttnd_user.html', context)

        except Taikhoan.DoesNotExist:
            return render(request, 'error.html', {'message': 'Tài khoản không tồn tại.'})
    else:
        return render(request, 'error.html', {'message': 'Người dùng chưa đăng nhập.'})