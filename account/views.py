from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from actions.models import Action
from actions.utils import create_action
from images.models import Contact
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if self.request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


# Create your views here.
def register(request):
    """
    Register a new user
    :param request:
    :return:
    """
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': user_form})


def user_login(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disable account')
            else:
                return HttpResponse('Invalid login')
    else:
        if request.user.is_authenticated:
            return reverse('dashboard')
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    """

    :param request:
    :return:
    """
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list(
        'id', flat=True
    )
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related(
        'user', 'user__profile'
    ).prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})


@login_required
def edit(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, "Error updating your profile")
        return render(request, 'account/dashboard.html', {'section': 'dashboard'})
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


User = get_user_model()


@login_required
def user_list(request):
    """
    List users
    :param request:
    :return:
    """
    users = User.objects.filter(is_active=True)
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required
def user_detail(request, username):
    """
    User detail
    :param request:
    :param username:
    :return:
    """
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        'account/user/detail.html',
        {'section': 'people', 'user': user}
    )


@require_POST
@login_required
def user_follow(request):
    """
    User Follow
    :param request:
    :return:
    """
    user_id = request.POST.get('id')
    action = request.POST.get('action')

    ''' if user_id == request.user.id:
        return JsonResponse({'status':'error'}) '''

    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user
                ).delete()
            return JsonResponse({'status': "ok"})
        except User.DoesNotExists:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
