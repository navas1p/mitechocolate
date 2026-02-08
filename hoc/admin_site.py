from django.contrib.admin import AdminSite
from django.urls import path

from core.admin_ai import assistant_view


class HOCAdminSite(AdminSite):
    site_header = "Heart of Chocolate Admin"
    site_title = "Heart of Chocolate Admin"
    index_title = "Administration"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("assistant/", self.admin_view(assistant_view), name="assistant"),
        ]
        return custom + urls


admin_site = HOCAdminSite()
