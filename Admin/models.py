from datetime import date, timedelta
from django.db import models
from django.conf import settings
import json
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    media = models.FileField(upload_to='news_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_image(self):
        # Kiểm tra nếu file là ảnh
        if self.media:
            return self.media.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        return False

    def is_video(self):
        # Kiểm tra nếu file là video
        if self.media:
            return self.media.name.lower().endswith(('.mp4', '.avi', '.mov'))
        return False



class Taikhoan(models.Model):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('manage', 'manage'),
        ('user', 'user'),
    )

    id = models.AutoField(primary_key=True)
    tai_khoan = models.CharField(max_length=100, unique=True)
    mat_khau = models.CharField(max_length=100)
    phan_quyen = models.CharField(max_length=10, choices=ROLE_CHOICES)
    khachhang = models.OneToOneField('Khachhang', on_delete=models.CASCADE, null=True, blank=True)
    last_activity = models.DateTimeField(default=timezone.now)  # Thêm trường để theo dõi hoạt động
    is_active = models.BooleanField(default=True)  # Trạng thái kích hoạt tài khoản
    activation_code = models.CharField(max_length=50, null=True, blank=True)  # Mã kích hoạt cho admin

    class Meta:
        db_table = 'tai_khoan'

    def __str__(self):
        return self.tai_khoan


class Congtybaohiem(models.Model):
    Ten_cong_ty= models.CharField(max_length=100)
    class Meta:
        db_table = 'cong_ty_bao_hiem'

class Danhgia(models.Model):
    Loai_KH= models.CharField(max_length=100)
    class Meta:
        db_table = 'Danh_gia'

class Doi(models.Model):
    ten_doi = models.CharField(max_length=255)
    quan_ly = models.ForeignKey(Taikhoan, on_delete=models.CASCADE, related_name='doi_quan_ly')  # Thay đổi ở đây
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ten_doi
    
class Khachhang(models.Model):
    ho_va_ten = models.CharField(max_length=255)
    ngay_sinh = models.DateField(default='2000-01-01')
    so_dien_thoai = models.CharField(max_length=20, unique=True)  # Đảm bảo số điện thoại là duy nhất
    dia_chi = models.CharField(max_length=255)
    cong_ty_bao_hiem = models.ManyToManyField('Congtybaohiem')
    tham_gia_bao_hiem = models.BooleanField(default=False)
    chi_tiet_bao_hiem = models.TextField()
    danh_gia = models.ForeignKey('Danhgia', on_delete=models.SET_NULL, null=True)
    IS_VIP = models.BooleanField(default=False)
    allowed_lessons = models.ManyToManyField('Lesson', blank=True)
    doi = models.ForeignKey(Doi, on_delete=models.SET_NULL, null=True, blank=True, related_name='khachhang_thuoc_doi')  # Chỉ định lại kiểu quan hệ
    quan_ly = models.ForeignKey(Taikhoan, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'phan_quyen': 'manage'}, related_name='khachhang_quan_ly')  # Chỉ định lại tên related_name

    def __str__(self):
        return self.ho_va_ten

    class Meta:
        db_table = 'khach_hang'


# Model lần gặp riêng biệt
class LanGap(models.Model):
    khach_hang = models.ForeignKey(Khachhang, on_delete=models.CASCADE, related_name='lan_gaps')
    noi_dung = models.TextField()

    def __str__(self):
        return self.khach_hang.ho_va_ten
            
class media(models.Model):
    ten = models.CharField(max_length=100)
    link = models.URLField()
    acp = models.BooleanField(default=False) 

    def __str__(self):
        return self.ten

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    ppt = models.FileField(upload_to='ppts/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    vip_only = models.BooleanField(default=False)  # Bài học chỉ dành cho VIP

class Lesson_KN(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    ppt = models.FileField(upload_to='ppts/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    vip_only = models.BooleanField(default=False)  # Bài học chỉ dành cho VIP

class Slide(models.Model):
    name = models.CharField(max_length=255)  # Tên slide
    file_url = models.CharField(max_length=255)  # URL của file PDF

    def __str__(self):
        return self.name
    
class Message(models.Model):
    sender = models.ForeignKey('Taikhoan', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('Taikhoan', on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    
    class Meta:
        db_table = 'message'