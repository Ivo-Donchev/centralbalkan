import os
from django.views.generic import TemplateView, FormView, View
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http.response import HttpResponse

from central_balkan.dashboard.models import SlideShowImage, Question
from central_balkan.dashboard.forms import AskQuestionForm

from central_balkan.products.models import Category, Product


class MainPageView(TemplateView):
    template_name = 'dashboard/main_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['images'] = [
            {
                'idx': idx,
                'url': image.image_url,
                'active_class': 'active' if idx == 0 else ''

            }
            for idx, image in enumerate(SlideShowImage.objects.all())
        ]

        return context


class CategoryDetailView(TemplateView):
    template_name = 'dashboard/category_detail.html'

    def get_products_rows(self, products, row_length):
        """
        Splits products into chunks
        """

        for i in range(0, len(products), row_length):
            yield products[i:i + row_length]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        category = get_object_or_404(
            Category.objects.prefetch_related('products'),
            slug=self.kwargs['category_slug']
        )

        context['category'] = category

        products_rows = self.get_products_rows(
            products=category.products.all(),
            row_length=3
        )

        context['products_rows'] = products_rows

        return context


class AskQuestionView(FormView):
    form_class = AskQuestionForm

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def form_valid(self, form):
        question = Question.objects.create(
            email=form.cleaned_data['email'],
            message=form.cleaned_data['message'],
        )

        product_id = form.cleaned_data.get('product')

        if product_id:
            product = Product.objects.get(id=product_id)
            question.product = product
            question.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Вие успешно изпратихте запитване. Очаквайте обратна връзка на "{}".'.format(question.email)
        )

        return super().form_valid(form)


class AboutUsView(TemplateView):
    template_name = 'dashboard/about_us.html'


class AppView(TemplateView):
    template_name = 'dashboard/app.html'
