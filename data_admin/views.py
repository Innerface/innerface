from django.shortcuts import HttpResponseRedirect, reverse
from django.views.generic import TemplateView
from data_admin.models import Synonyms, Emotional, Sensitive
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from chatbot.settings import PICKLE_DIR
import datetime
import pickle


# Create your views here.
from tools.utils import pages


class SynonymsView(LoginRequiredMixin, TemplateView):
    template_name = 'hm_admin/synonyms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = Synonyms.objects.all()
        # 分页展示
        context = pages(obj, self.request, context)
        return context

    def post(self, request):
        action = request.POST.get('action', '')
        if action == 'delete':
            synonyms_id = request.POST.get('synonyms_id', '')
            Synonyms.objects.filter(id=synonyms_id).delete()
        else:
            word = request.POST.get('word')
            parent_id = request.POST.get('parent_id')
            count = int(request.POST.get('count'))
            status = int(request.POST.get('status'))
            create_time = datetime.datetime.now()
            if action == 'add':
                Synonyms.objects.get_or_create(word=word, parent_id=parent_id, count=count, status=status,
                                               create_time=create_time)
            elif action == 'change':
                synonyms_id = request.POST.get('synonyms_id')
                Synonyms.objects.filter(id=synonyms_id).update(**{'word': word, 'parent_id': parent_id,
                                                                  'count': count, 'status': status,
                                                                  'create_time': create_time})
            else:
                pass
        return HttpResponseRedirect(reverse('synonyms'))


class EmotionalView(LoginRequiredMixin, TemplateView):
    template_name = 'hm_admin/emotional.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = Emotional.objects.all()
        context['obj'] = obj
        context = pages(obj, self.request, context)
        return context

    def post(self, request):
        action = request.POST.get('action', '')
        if action == 'delete':
            emotional_id = request.POST.get('emotional_id', '')
            Emotional.objects.filter(id=emotional_id).delete()
        else:
            word = request.POST.get('word')
            table_type = request.POST.get('table_type')
            emotion_type = request.POST.get('emotion_type')
            count = int(request.POST.get('count'))
            status = int(request.POST.get('status'))
            create_time = datetime.datetime.now()
            if action == 'add':
                Emotional.objects.get_or_create(word=word, table_type=table_type, emotion_type=emotion_type,
                                                count=count, status=status, create_time=create_time)
            elif action == 'change':
                emotional_id = request.POST.get('emotional_id')
                Emotional.objects.filter(id=emotional_id).update(**{'word': word, 'table_type': table_type,
                                                                    'emotion_type': emotion_type, 'count': count,
                                                                    'status': status, 'create_time': create_time})
            else:
                pass
        return HttpResponseRedirect(reverse('emotional'))


class SensitiveView(LoginRequiredMixin, TemplateView):
    template_name = 'hm_admin/sensitive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = Sensitive.objects.all()
        context['obj'] = obj
        context = pages(obj, self.request, context)
        return context

    def post(self, request):
        action = request.POST.get('action', '')
        if action == 'delete':
            sensitive_id = request.POST.get('sensitive_id', '')
            Sensitive.objects.filter(id=sensitive_id).delete()
        else:
            word = request.POST.get('word')
            table_type = request.POST.get('table_type')
            count = int(request.POST.get('count'))
            status = int(request.POST.get('status'))
            create_time = datetime.datetime.now()
            if action == 'add':
                Sensitive.objects.get_or_create(word=word, table_type=table_type, count=count, status=status,
                                                create_time=create_time)
            elif action == 'change':
                sensitive_id = request.POST.get('sensitive_id')
                Sensitive.objects.filter(id=sensitive_id).update(**{'word': word, 'table_type': table_type,
                                                                    'count': count, 'status': status,
                                                                    'create_time': create_time})
            else:
                pass
        return HttpResponseRedirect(reverse('sensitive'))


@login_required
def sensitive_init(request):
    from chatbot.core import sensitiveWord
    sensitiveWord.init()
    return HttpResponseRedirect(reverse('sensitive'))


@login_required
def synonyms_init(request):
    synonsyms = {}
    parent_synonsyms = {}
    for synonsym in Synonyms.objects.all():
        if synonsym.parent_id:
            synonsyms[synonsym.word] = str(synonsym.parent_id)
        else:
            parent_synonsyms[str(synonsym.id)] = synonsym.word
    for word, parent_id in synonsyms.items():
        synonsyms[word] = parent_synonsyms[parent_id]
    f = open(PICKLE_DIR/'synonyms.pickle', 'wb')
    pickle.dump(synonsyms, f, True)
    return HttpResponseRedirect(reverse('synonyms'))


@login_required
def synonyms_file_update(request):
    import pathlib
    from django.http import HttpResponse
    f_path = pathlib.Path.cwd()/'vendor'/'dataset'/'chinese'/'synonym.txt'
    insert_list = []
    count = 1
    with open(f_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            synonyms_list = line.split()
            synonym_value = synonyms_list[0]
            synonym_key = synonyms_list[1:]
            insert_list.append(Synonyms(word=synonym_value, parent_id=0, count=0, status=0, create_time=datetime.datetime.now()))
            for k in synonym_key:
                insert_list.append(Synonyms(word=k, parent_id=count, count=0, status=0, create_time=datetime.datetime.now()))
            count += len(synonyms_list)

            print('############')
            print(f'synonym_key:{synonym_key},synonym_value:{synonym_value}，parent_id:{count}')

    Synonyms.objects.bulk_create(insert_list)
    return HttpResponse('synonyms_file_update')


def test(request):
    from django.http import HttpResponse, JsonResponse
    from urllib.parse import unquote
    from vendor.optimization import keywords_sorted as doks
    from chatbot.core.generate_model import synonymous_sentence_matching
    # synonyms = doks.default_synonyms()
    ques = request.GET.get('word')
    # syn = ''
    # for k, v in synonyms.items():
    #     if k == word:
    #         syn = v
    # print(syn)
    # ques = request.GET.get('question', '')
    answer = synonymous_sentence_matching(ques)
    print(f'question:{ques}, answer:{answer}')
    return HttpResponse(answer)
