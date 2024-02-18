from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_http_methods
from foogal.models import File, Setting, Link
from django.contrib.auth.decorators import login_required
import json
import os
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(['POST'])
def handle_upload(request):
    if request.method == 'POST':
        valid_files = ['txt', 'pdf']
        ds = Setting.objects.get(name=settings.DEFAULT_CONF_SETTING)
        ret = {'status': 'success', 'msg': ''}
        folder = os.path.join(settings.MEDIA_ROOT, settings.DEFAULT_CONF_SETTING)
        if not os.path.exists(folder):
            os.makedirs(folder)
        fs = FileSystemStorage(location=folder)
        files = [request.FILES.get(f'file[{i}]') for i in range(0, len(request.FILES))]
        for file in files:
            if file.name.split('.')[-1] not in valid_files:
                continue
            try:
                filename = fs.save(file.name, file)
                File.objects.create(settings=ds, file_name=filename, file_path=fs.path(filename), file_size=file.size)
            except Exception as e:
                logger.error(f'Failed to save file {e}', exc_info=True)
                ret['status'] = 'fail'
                ret['msg'] = 'Failed to save file'
                break

        return JsonResponse(ret)


@login_required
@require_http_methods(['GET'])
def handle_settings(request):
    if request.method == 'GET':
        ret = {'status': 'success', 'msg': '', 'filenames': []}
        try:
            ds, created = Setting.objects.get_or_create(name=settings.DEFAULT_CONF_SETTING)
            qs = File.objects.filter(settings=ds).all()
            file_names = list(qs.values('file_name', 'file_size'))
        except Exception as e:
            logger.error(f'Failed to retrieve files {e}', exc_info=True)
            ret['status'] = 'fail'
            ret['msg'] = 'Failed to retrieve files'
        ret['filenames'] = file_names

        return JsonResponse(ret)


@login_required
@require_http_methods(['POST'])
def remove_files(request):
    if request.method == 'POST':
        params = json.loads(request.body)
        filename = params.get("filename")
        fs = FileSystemStorage()
        ret = 'success'
        if filename:
            try:
                file = File.objects.get(file_name=filename)
                if file:
                    path = file.file_path
                    if fs.exists(path):
                        fs.delete(path)
                        file.delete()
            except Exception as e:
                logger.log(f'Failed to delete file {e}', exc_info=True)
                ret = 'failed'

        return HttpResponse(ret)


@login_required
@require_http_methods(['GET', 'POST'])
def handle_links(request):
    if request.method == 'GET':
        try:
            ds = Setting.objects.get(name=settings.DEFAULT_CONF_SETTING)
            qs = Link.objects.filter(settings=ds)
            urls = [link.url for link in qs]
            ret = {'setting': settings.DEFAULT_CONF_SETTING, 'urls': ','.join(urls)}
            return JsonResponse(ret)
        except Exception as e:
            logger.error(f'Failed to get url links {e}', exc_info=True)
            return JsonResponse({'setting': settings.DEFAULT_CONF_SETTING, 'urls': ''})
    if request.method == 'POST':
        params = json.loads(request.body)
        try:
            ds = Setting.objects.get(name=params['setting'])
            obj, created = Link.objects.get_or_create(settings=ds)
            obj.url = params['urls']
            obj.save()
            return JsonResponse(params)
        except Exception as e:
            logger.error(f'Failed to save url links {e}', exc_info=True)
            qs = Link.objects.filter(settings=ds)
            urls = [link.url for link in qs]
            ret = {'setting': params['setting'], 'urls': ','.join(urls)}
            return JsonResponse(ret)
