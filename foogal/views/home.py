
import os

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from foogal.models import Setting, Link, Config
from langchain_community.document_loaders import TextLoader, DirectoryLoader, WikipediaLoader
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import platform
import asyncio
import json
import logging
import aiohttp
import re
import tempfile

logger = logging.getLogger(__name__)

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def landing_page(request):
    """
    Renders home page
    """
    configs = request.session.get('configs', {})
    configs['localset'] = settings.LOCAL_LINK_SETTING
    configs['defaultset'] = settings.DEFAULT_CONF_SETTING
    request.session['configs'] = configs
    path = os.path.join(settings.STATIC_ROOT, 'js') if os.path.exists(settings.STATIC_ROOT) else None
    js_files = [
        f for f in os.listdir(path) if f.endswith('.js') and f not in settings.JS_INIT_FILES
    ] if path and os.path.isdir(path) else []

    if settings.DEBUG:
        # get source from uncompressed .js to debug
        apps = ['foogal']
        for app in apps:
            path = os.path.join(settings.BASE_DIR, f'{app}/static/js')
            js_files = [f for f in os.listdir(path) if f.endswith('.js') and f not in settings.JS_INIT_FILES]

    response = render(request, 'home.html', {
        'content': 'base',
        'files': settings.JS_INIT_FILES + js_files
    })
    return response


@require_http_methods(['GET', 'POST'])
def handle_local_links(request):
    if request.method == 'GET':
        try:
            ds, created = Setting.objects.get_or_create(name=request.session.session_key)
            configs = request.session.get('configs', {})
            configs['localset'] = ds.name
            request.session['configs'] = configs
            qs = Link.objects.filter(settings=ds)
            urls = [link.url for link in qs]
            ret = {'setting': request.session.session_key, 'urls': ','.join(urls)}
            return JsonResponse(ret)
        except Exception as e:
            logger.error(f'Failed to get local url links {e}', exc_info=True)
            return JsonResponse({'setting': request.session.session_key, 'urls': ''})
    if request.method == 'POST':
        params = json.loads(request.body)
        try:
            ds = Setting.objects.get(name=request.session.session_key)
            obj, created = Link.objects.get_or_create(settings=ds)
            obj.url = params['urls']
            obj.save()
            ret = {'setting': request.session.session_key, 'urls': params['urls']}
            return JsonResponse(ret)
        except Exception as e:
            logger.error(f'Failed to save local url links {e}', exc_info=True)
            qs = Link.objects.filter(settings=ds)
            urls = [link.url for link in qs]
            ret = {'setting': request.session.session_key, 'urls': ','.join(urls)}
            return JsonResponse(ret)


@require_http_methods(['POST'])
def handle_asks(request):
    params = json.loads(request.body)
    common_loader = []
    configs = request.session.get('configs', {})
    ds = Setting.objects.get(name=settings.DEFAULT_CONF_SETTING)
    localset = Setting.objects.filter(name=request.session.session_key)
    folder_path = os.path.join(settings.MEDIA_ROOT, settings.DEFAULT_CONF_SETTING)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    loader = DirectoryLoader(folder_path, silent_errors=True)
    common_loader.append(loader)
    quest = params.get("ask")
    ret = {'data': {}, 'status': 'fail', 'msg': ''}
    try:
        qs = Link.objects.filter(settings=ds)
        localqs = Link.objects.filter(settings=localset[0]) if localset else []
        urls = [link.url for link in qs if link.url != '']
        urls += [link.url for link in localqs if link.url != '']

        def loadurl(url_list):
            try:
                loader = None
                scrape_data = []
                loader = WebBaseLoader(url_list, continue_on_failure=True)
                scrape_data = loader.aload()

            except Exception as e:
                if isinstance(e, aiohttp.InvalidURL):
                    try:
                        initial_len = len(url_list)
                        url_list.remove(str(e))
                        new_len = len(url_list)
                        if new_len < initial_len:
                            scrape_data, loader = loadurl(url_list)
                    except Exception as e:
                        logger.error(f'Failed to exclude invalid url {e}', exc_info=True)
                if isinstance(e, aiohttp.ClientConnectionError):
                    try:
                        initial_len = len(url_list)
                        url_list= [url for url in url_list if e.host not in url]
                        new_len = len(url_list)
                        if new_len < initial_len:
                            scrape_data, loader = loadurl(url_list)
                    except Exception as e:
                        logger.error(f'Failed to exclude unreachable url  {e}', exc_info=True)
                else:
                    logger.error(f'Failed to load url content {e}', exc_info=True)
            return scrape_data, loader
        scrape_data, loader = loadurl(urls)
        if len(scrape_data) > 0:
            common_loader.append(loader)
        if configs.get('wiki_enabled'):
            #load from wikipedia
            loader = WikipediaLoader(quest)
            common_loader.append(loader)
        try:
            index = VectorstoreIndexCreator().from_loaders(common_loader)
        except Exception as e:
            index = None
            logger.error(f'Failed to create langchain index {e}', exc_info=True)
        scope = request.user.config.filter(name='scope') if request.user.is_authenticated else None
        llm = ChatOpenAI(temperature=0, max_tokens=3000)
        if index:
            if scope and scope.exists() and scope[0].value == 'internal':
                resp = index.query(quest)
            else:
                resp = index.query(quest, llm=llm)
        else:
            resp = llm.invoke(quest).content

        logger.info(f'Generated response: {resp}')
        ret['data'] = {'response': resp}
        ret['status'] = 'success'

    except Exception as e:
        logger.error(f'Error in handling ask {e}', exc_info=True)
        ret['msg'] = 'Failed to generate response. Please try again'

    return JsonResponse(ret)
