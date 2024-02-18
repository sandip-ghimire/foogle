from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import os
import json
import logging

logger = logging.getLogger(__name__)


@require_http_methods(['GET', 'POST'])
def config(request):
    if request.method == 'GET':
        configs = request.session.get('configs') or {}
        return JsonResponse(configs)
    if request.method == 'POST':
        try:
            configs = json.loads(request.body)
            request.session['configs'] = configs
            return JsonResponse(configs)
        except Exception as e:
            logger.error(f'Failed to save config {e}', exc_info=True)
            return JsonResponse(request.session.get('configs') or {})


@login_required
@require_http_methods(['GET', 'POST'])
def user_config(request):
    if request.method == 'GET':
        qs = request.user.config.all()
        configs = {i['name']: i['value'] for i in qs.values('name', 'value')}
        return JsonResponse(configs)
    if request.method == 'POST':
        try:
            configs = json.loads(request.body)
            for k, v in configs.items():
                obj, created = request.user.config.get_or_create(name=k)
                obj.value = v
                obj.save()
            return JsonResponse(configs)
        except Exception as e:
            logger.error(f'Failed to save user config {e}', exc_info=True)
            qs = request.user.config.all()
            ret = {i['name']: i['value'] for i in qs.values('name', 'value')}
            return JsonResponse(ret)
