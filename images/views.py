import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


# Create your views here.
@login_required
def image_create(request):
    """
    View for creating an image using the JavaScript Bookmarklet.
    :param request:
    :return:
    """
    if request.method == 'POST':
        image_form = ImageCreateForm(data=request.POST)
        if image_form.is_valid():
            cd = image_form.cleaned_data
            new_image = image_form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            created_action = create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())
    else:
        image_form = ImageCreateForm(data=request.GET)

    return render(request, 'images/image/create.html', {'form': image_form, 'section': 'images'})


@login_required
def image_detail(request, id, slug):
    """
    View for viewing an image.
    :param request:
    :return:
    """
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total image views by 1
    total_views = r.incr(f'image:{image.id}:views')
    r.zincrby('image_ranking', 1, image.id)
    return render(request, 'images/image/detail.html',
                  {'section': 'images', "image": image, 'total_views': total_views})


@login_required
@require_POST
def image_like(request):
    """
    Image like, unlike view
    :param request:
    :return:
    """
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    """
    Image list paginator
    :param request:
    :return:
    """
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    """

    :param request:
    :return:
    """
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(image_id) for image_id in image_ranking]
    most_viewed = list(
        Image.objects.filter(id__in=image_ranking_ids)
    )
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

    return render(request, 'images/image/ranking.html', {'most_viewed': most_viewed})
