from django import forms
from django.contrib import admin
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from simple_history.admin import SimpleHistoryAdmin

from core.admin_utils import custom_titled_filter
from .models import Author, Book, Page


@admin.register(Author)
class AuthrAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["name", "author", 'status', 'pages_count', 'pages_processing_count', 'pages_ready_count',
                    'pages_in_progress_count', 'pages_done_count']
    list_filter = ['author']
    search_fields = ['name', 'author__name']
    readonly_fields = ['status', 'pages_count', 'pages_processing_count', 'pages_ready_count',
                       'pages_in_progress_count', 'pages_done_count']
    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'pdf')
        }),
    )
    autocomplete_fields = ['author']

    def get_queryset(self, request):
        # annotate pages count for each page status
        return super().get_queryset(request).annotate(
            pages_count=models.Count('pages'),
            pages_processing_count=models.Count('pages', filter=models.Q(pages__status=Page.Status.PROCESSING)),
            pages_ready_count=models.Count('pages', filter=models.Q(pages__status=Page.Status.READY)),
            pages_in_progress_count=models.Count('pages', filter=models.Q(pages__status=Page.Status.IN_PROGRESS)),
            pages_done_count=models.Count('pages', filter=models.Q(pages__status=Page.Status.DONE)),
        )

    def status(self, obj):
        if obj.pages_ready_count < obj.pages_count:
            return 'Идет распознавание'
        elif obj.pages_done_count == obj.pages_count:
            return 'Вычитано'
        else:
            return 'В процессе вычитки'

    def pages_count(self, obj):
        return obj.pages_count

    def pages_processing_count(self, obj):
        return obj.pages_processing_count

    def pages_ready_count(self, obj):
        return obj.pages_ready_count

    def pages_in_progress_count(self, obj):
        return obj.pages_in_progress_count

    def pages_done_count(self, obj):
        return obj.pages_done_count
    

class PageAdminForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'resizeable-textarea', 'rows': 60, 'cols': 80}),
        label='Your Text'
    )

    text_size = forms.IntegerField(
        label='Text Size (px)',
        widget=forms.NumberInput(attrs={'id': 'text-size-input'}),
    )

    class Meta:
        model = Page
        fields = '__all__'


@admin.register(Page)
class PageAdmin(SimpleHistoryAdmin):
    form = PageAdminForm
    change_form_template = "admin/page_change_form.html"
    list_display = ["number", "book", "modified", 'status']
    history_list_display = ["text"]
    readonly_fields = ['book', 'page', 'number']
    fieldsets = (
        (None, {
            'fields': ('book', 'number', 'status', 'text_size')
        }),
        ('Редактирование', {
            'fields': (('text', 'page'),)
        }),
    )
    list_filter = [('book__name', custom_titled_filter('Book')), 'status']

    def page(self, obj):
        if obj.image:
            image_url = obj.image.url
            return mark_safe(
                f'<a href="{image_url}" data-fancybox="images" data-caption="page">'
                f'<img src="{image_url}" width="600" /></a>'
            )
        return '-'

    def _get_context(self, request, object_id=None) -> dict:
        obj = self.get_object(request, object_id)
        extra_context = {
            'prev_page_exists': Page.objects.filter(book=obj.book, number=obj.number - 1).exists(),
            'next_page_exists': Page.objects.filter(book=obj.book, number=obj.number + 1).exists(),
        }

        return extra_context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self._get_context(request, object_id))
        return self.changeform_view(request, object_id, form_url, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        current_page = self.get_object(request, object_id)
        if f'back_page' in request.POST:
            prev_page = Page.objects.filter(book=current_page.book, number=current_page.number - 1).last()
            return redirect(reverse("admin:books_page_change", args=(prev_page.id,)))

        elif f'next_page' in request.POST:
            next_page = Page.objects.filter(book=current_page.book, number=current_page.number + 1).last()
            return redirect(reverse("admin:books_page_change", args=(next_page.id,)))

        return super().changeform_view(request, object_id, form_url, extra_context)  # noqa
