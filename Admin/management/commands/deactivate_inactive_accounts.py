from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from models import Taikhoan

class Command(BaseCommand):
    help = 'Vô hiệu hóa tài khoản không hoạt động trong 12 tháng'

    def handle(self, *args, **kwargs):
        # Lấy thời điểm hiện tại
        now = timezone.now()
        # Xác định thời gian giới hạn 12 tháng
        inactivity_threshold = now - timedelta(days=365)
        
        # Lọc các tài khoản không hoạt động và vẫn đang kích hoạt
        inactive_accounts = Taikhoan.objects.filter(last_activity__lt=inactivity_threshold, is_active=True)

        # Vô hiệu hóa các tài khoản
        for account in inactive_accounts:
            account.is_active = False
            account.save()
            self.stdout.write(self.style.SUCCESS(f'Tài khoản {account.tai_khoan} đã bị vô hiệu hóa do không hoạt động.'))

        if not inactive_accounts.exists():
            self.stdout.write(self.style.SUCCESS('Không có tài khoản nào cần vô hiệu hóa.'))
