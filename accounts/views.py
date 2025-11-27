
import os
import requests
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .utils import jwt_login_required



def user_access(request):
    return render(request, "accounts/rights_access.html")

@jwt_login_required
def user_flow(request):
    return render(request, "accounts/user_flow.html")

def logout_view(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('refresh_token')
    return response


@csrf_exempt        
@require_POST
def groq_chat_proxy(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"  
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            return JsonResponse({
                'error': 'Groq API error',
                'details': response.text
            }, status=response.status_code)

        groq_data = response.json()
        bot_reply = groq_data['choices'][0]['message']['content']

        return JsonResponse({'reply': bot_reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)







