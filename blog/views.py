import datetime
import base64
import io
import os
import re
import anthropic
from PIL import Image

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import MushroomDetail, MushroomPhoto


IDENTIFY_SYSTEM_PROMPT = (
    "You are an expert mycologist assistant. "
    "When shown photos of mushrooms, provide: 1) Most likely species "
    "(common name and latin name), 2) Key identifying features visible "
    "in the photos, 3) Confidence level (High/Medium/Low), 4) Edibility "
    "and safety notes, 5) Similar species to rule out. Always include a "
    "disclaimer that AI identification should be verified by an expert "
    "before handling or consuming any wild mushroom."
)

PREFERRED_IDENTIFY_MODELS = [
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20240620',
    'claude-3-5-haiku-20241022',
    'claude-3-haiku-20240307',
    'claude-3-opus-20240229',
]


def _extract_latin_name(text):
    labeled = re.search(
        r"(latin name|scientific name)\s*[:\-]\s*([A-Z][a-z]+(?:\s+[a-z][a-z\-]+){1,2})",
        text,
        flags=re.IGNORECASE,
    )
    if labeled:
        return labeled.group(2).strip()

    binomial = re.search(r"\b([A-Z][a-z]+(?:\s+[a-z][a-z\-]+){1,2})\b", text)
    if binomial:
        return binomial.group(1).strip()
    return ""


def _select_available_model(client):
    """
    Choose a model that actually exists for this API key/account.
    Returns (model_name, available_model_ids).
    """
    available_ids = []
    try:
        model_page = client.models.list(limit=50)
        for model in model_page.data:
            model_id = getattr(model, 'id', None)
            if model_id:
                available_ids.append(model_id)
    except Exception:
        return None, []

    for preferred in PREFERRED_IDENTIFY_MODELS:
        if preferred in available_ids:
            return preferred, available_ids

    for model_id in available_ids:
        if model_id.startswith('claude-'):
            return model_id, available_ids

    return None, available_ids


def all_blogs(request):
    mushrooms_detail = MushroomDetail.objects.all()
    return render(request, 'blog/all_blogs.html', {'mushrooms_detail': mushrooms_detail})


def detail(request, blog_id):
    blog = get_object_or_404(MushroomDetail, pk=blog_id)
    return render(request, 'blog/detail.html', {'blog': blog})


def map_page(request):
    MushroomDetails = MushroomDetail.objects.all()
    return render(request, 'blog/map_page.html', {'MushroomDetails': MushroomDetails})


def about(request):
    return render(request, 'blog/about.html')


@login_required
def identify(request):
    if request.method != 'POST':
        return JsonResponse(
            {
                'success': False,
                'identification': '',
                'latin_name': '',
                'error': 'Method not allowed. Use POST.',
            },
            status=405,
        )

    try:
        photos = request.FILES.getlist('photos')
        if not photos:
            return JsonResponse(
                {
                    'success': False,
                    'identification': '',
                    'latin_name': '',
                    'error': 'Please upload at least one photo.',
                },
                status=400,
            )

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return JsonResponse(
                {
                    'success': False,
                    'identification': '',
                    'latin_name': '',
                    'error': 'ANTHROPIC_API_KEY is not configured.',
                },
                status=500,
            )

        content_blocks = [
            {'type': 'text', 'text': 'Please identify the mushroom(s) in these photos.'}
        ]
        for photo in photos:
            img = Image.open(photo)
            max_size = 1200
            ratio = min(max_size / img.width, max_size / img.height, 1.0)
            if ratio < 1.0:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            media_type = 'image/jpeg'
            content_blocks.append(
                {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': media_type,
                        'data': encoded,
                    },
                }
            )

        client = anthropic.Anthropic(api_key=api_key)
        selected_model, available_models = _select_available_model(client)
        if not selected_model:
            return JsonResponse(
                {
                    'success': False,
                    'identification': '',
                    'latin_name': '',
                    'error': (
                        'No usable Anthropic model found for this API key. '
                        f'Available models: {", ".join(available_models) if available_models else "none returned"}'
                    ),
                },
                status=502,
            )

        response = client.messages.create(
            model=selected_model,
            max_tokens=900,
            system=IDENTIFY_SYSTEM_PROMPT,
            messages=[
                {
                    'role': 'user',
                    'content': content_blocks,
                }
            ],
        )

        identification_text = ""
        for block in response.content:
            if getattr(block, 'type', None) == 'text':
                identification_text += block.text

        identification_text = identification_text.strip()
        latin_name = _extract_latin_name(identification_text)

        return JsonResponse(
            {
                'success': True,
                'identification': identification_text,
                'latin_name': latin_name,
                'error': '',
            }
        )
    except Exception as exc:
        return JsonResponse(
            {
                'success': False,
                'identification': '',
                'latin_name': '',
                'error': str(exc),
            },
            status=500,
        )


@login_required
def new_find(request):
    today = datetime.date.today()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        latin_name = request.POST.get('latin_name', '').strip()
        description = request.POST.get('description', '').strip()
        ai_identification = request.POST.get('ai_identification', '').strip()
        date_raw = request.POST.get('date')
        photos = request.FILES.getlist('photos')

        if not title or not latin_name:
            messages.error(request, 'Title and Latin name are required.')
            return render(request, 'blog/new_find.html', {'today': today})

        if not photos:
            messages.error(request, 'Please add at least one photo.')
            return render(request, 'blog/new_find.html', {'today': today})

        try:
            if date_raw:
                find_date = datetime.datetime.strptime(date_raw, '%Y-%m-%d').date()
            else:
                find_date = today
        except ValueError:
            find_date = today

        for f in photos:
            f.seek(0)

        mushroom = MushroomDetail.objects.create(
            title=title,
            latin_name=latin_name,
            description=description,
            ai_identification=ai_identification,
            date=find_date,
            image=photos[0],
        )

        for i, f in enumerate(photos):
            f.seek(0)
            MushroomPhoto.objects.create(
                mushroom=mushroom,
                image=f,
                order=i,
            )

        messages.success(request, 'Mushroom find saved.')
        return redirect('blog:detail', blog_id=mushroom.pk)

    return render(request, 'blog/new_find.html', {'today': today})
