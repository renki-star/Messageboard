from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Message

# 🔹 Tarkistetaan, onko käyttäjä moderaattori (admin tai staff)
def is_moderator(user):
    return user.is_authenticated and user.is_staff

# 🔹 Kirjautumisnäkymä
def login_view(request):
    if request.user.is_authenticated:  # Jos käyttäjä on jo kirjautunut, ohjaa moderaattorinäkymään
        return redirect('moderator_view')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('moderator_view')  # Kirjautumisen jälkeen siirrytään moderaattorinäkymään
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# 🔹 Uloskirjautumisnäkymä
def logout_view(request):
    logout(request)
    return redirect('login')

# 🔹 Viestiseinän näkymä (käyttäjille)
def message_board(request):
    if request.method == "POST":
        username = request.POST.get("username")
        text = request.POST.get("text")
        if username and text:
            Message.objects.create(username=username, text=text, approved=False)  # Viestit odottavat hyväksyntää
    messages = Message.objects.filter(approved=True).order_by("-timestamp")
    return render(request, "messageboard.html", {"messages": messages})

# 🔹 Hakee hyväksytyt viestit JSON-muodossa (AJAX-päivitystä varten)
def get_approved_messages(request):
    messages = Message.objects.filter(approved=True).order_by("-timestamp")
    messages_data = [{"id": msg.id, "username": msg.username, "text": msg.text} for msg in messages]
    return JsonResponse({"messages": messages_data})

# 🔹 Hakee julkaisemattomat viestit JSON-muodossa (Moderaattorin hallintaan)
def get_pending_messages(request):
    messages = Message.objects.filter(approved=False).values("id", "username", "text")
    return JsonResponse({"messages": list(messages)})

# 🔹 Hyväksyy kaikki julkaisemattomat viestit
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def approve_all(request):
    try:
        Message.objects.filter(approved=False).update(approved=True)
        return JsonResponse({"status": "approved_all"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# 🔹 Poistaa kaikki julkaisemattomat viestit
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def delete_all_pending(request):
    try:
        Message.objects.filter(approved=False).delete()
        return JsonResponse({"status": "deleted_all_pending"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# 🔹 Poistaa kaikki julkaistut viestit
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def delete_all_published(request):
    try:
        Message.objects.filter(approved=True).delete()
        return JsonResponse({"status": "deleted_all_published"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# 🔹 Moderaattorin näkymä (vaatii kirjautumisen)
@login_required(login_url='/login/')
@user_passes_test(is_moderator, login_url='/login/')
def moderator_view(request):
    messages = Message.objects.all().order_by("-timestamp")  # Kaikki viestit
    return render(request, "moderator.html", {"messages": messages})

# 🔹 Hyväksy viesti
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def approve_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message.approved = True
        message.save()
        return JsonResponse({"status": "approved"})
    except Message.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Message not found"}, status=404)

# 🔹 Poista yksittäinen viesti
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message.delete()
        return JsonResponse({"status": "deleted"})
    except Message.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Message not found"}, status=404)

# 🔹 Poista kaikki viestit kerralla (Tyhjennä viestiseinä)
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def clear_messages(request):
    Message.objects.all().delete()
    return JsonResponse({"status": "cleared"})

# 🔹 Moderaattori voi lähettää viestejä viestiseinälle
@csrf_exempt
@login_required(login_url='/login/')
@user_passes_test(is_moderator)
def send_moderator_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message_text = data.get("text", "").strip()

            if not message_text:
                return JsonResponse({"status": "error", "message": "Viesti ei voi olla tyhjä."}, status=400)

            # Luo viesti automaattisesti hyväksyttynä
            Message.objects.create(username="Moderaattori", text=message_text, approved=True)

            return JsonResponse({"status": "sent"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Virhe viestin käsittelyssä."}, status=400)

    return JsonResponse({"status": "error", "message": "Väärä pyyntö."}, status=400)
