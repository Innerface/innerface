from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import HttpResponseRedirect, reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
import io
from suser.Helper import Checkcode
import logging
Logger = logging.getLogger('django')


# Create your views here.
class UserView(TemplateView):
    # login_url = 'index'
    # redirect_field_name = 'redirect_to'
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request):
        from chatbot.middleware.csrf import rotate_token
        rotate_token(request)
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            username = request.POST.get('username')
            password = request.POST.get('psw')
            check_code = request.POST.get('checkcode')
            error = ''
            try:
                session_code = request.session["CheckCode"]
            except KeyError:
                Logger.error('[Login]except KeyError')
                return HttpResponseRedirect(reverse('login'))
            request.session.set_expiry(14 * 60 * 60)
            if username and password:
                if check_code.strip().lower() == session_code.lower():
                    user = authenticate(username=username, password=password)
                    if user:
                        if user.is_active:
                            login(request, user)
                            return HttpResponseRedirect(request.session.get('pre_url', '/'))
                            # return HttpResponseRedirect(reverse('index'))
                        else:
                            error = u'用户未激活'
                    else:
                        Logger.error('[Login]username or password wrong')
                        error = u'用户名或密码错误'
                else:
                    Logger.error('[Login]except KeyError')
                    error = u'验证码错误'
            else:
                Logger.error('[Login]username or password is empty')
                error = u'用户名或密码不能为空'
            return HttpResponseRedirect(reverse('login'))


def CheckCode(request):
    mstream = io.BytesIO()
    validate_code = Checkcode.create_validate_code()
    img = validate_code[0]
    img.save(mstream, "GIF")
    # 将验证码保存到session
    request.session["CheckCode"] = validate_code[1]
    return HttpResponse(mstream.getvalue())


def Logout(request):
    logout(request)  # already flush session
    # design by django.contrib.sessions.middleware.SessionMiddleware
    try:
        del request.COOKIES["sessionid"]
        del request.session['sessionid']
    except KeyError:
        Logger.error(f'del sessionid error:{str(KeyError)}')
    return HttpResponseRedirect(reverse('login'))
