import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import AIModel, Assistant
from accounts.models import Transaction

import base64
from .models import AIModel, Assistant, ChatImage


def index(request):
    models = AIModel.objects.filter(is_active=True)
    assistants = Assistant.objects.filter(is_active=True)
    return render(request, 'chat/index.html', {
        'models': models,
        'assistants': assistants
    })


@csrf_exempt
def chat_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    if not request.user.can_send_message():
        return JsonResponse({
            'error': 'Недостаточно средств. Пополните баланс или используйте бесплатные сообщения.',
            'need_payment': True
        }, status=402)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        messages = data.get('messages', [])
        model_id = data.get('model_id')
        assistant_id = data.get('assistant_id')
        image_id = data.get('image_id')

        # Поддержка старого формата
        if not messages and data.get('message'):
            messages = [{'role': 'user', 'content': data.get('message')}]

        print(
            f"Получен запрос: model_id={model_id}, assistant_id={assistant_id}, messages={len(messages)}, image_id={image_id}")

        if not messages:
            return JsonResponse({'error': 'Сообщения не могут быть пустыми'}, status=400)

        # Получаем модель и ассистента
        try:
            model = AIModel.objects.get(id=model_id, is_active=True)
            print(f"Найдена модель: {model.name} ({model.api_name})")
        except AIModel.DoesNotExist:
            return JsonResponse({'error': 'Модель не найдена'}, status=400)

        assistant = None
        if assistant_id:
            try:
                assistant = Assistant.objects.get(id=assistant_id, is_active=True)
                print(f"Найден ассистент: {assistant.name}")
            except Assistant.DoesNotExist:
                pass

        # Формируем сообщения для API
        api_messages = []

        # Добавляем системное сообщение ассистента если есть
        if assistant:
            api_messages.append({
                "role": "system",
                "content": assistant.get_full_prompt()
            })

        # Добавляем историю разговора
        for msg in messages:
            api_messages.append(msg)

        # Обрабатываем изображение если есть
        if image_id:
            try:
                chat_image = ChatImage.objects.get(id=image_id)
                with open(chat_image.image.path, 'rb') as img_file:
                    image_base64 = base64.b64encode(img_file.read()).decode()

                # Модифицируем последнее пользовательское сообщение
                if api_messages and api_messages[-1]['role'] == 'user':
                    original_content = api_messages[-1]['content']

                    if model.provider == 'openai':
                        api_messages[-1]['content'] = [
                            {"type": "text", "text": original_content},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    elif model.provider == 'anthropic':
                        api_messages[-1]['content'] = [
                            {"type": "text", "text": original_content},
                            {"type": "image",
                             "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}}
                        ]

            except ChatImage.DoesNotExist:
                print("Изображение не найдено")
                pass
            except Exception as e:
                print(f"Ошибка обработки изображения: {str(e)}")
                pass

        # Получаем URL для провайдера
        provider_urls = {
            'openai': 'https://api.proxyapi.ru/openai/v1',
            'anthropic': 'https://api.proxyapi.ru/anthropic',
            'deepseek': 'https://api.proxyapi.ru/deepseek',
            'google': 'https://api.proxyapi.ru/google',
        }

        base_url = provider_urls.get(model.provider)
        if not base_url:
            return JsonResponse({'error': f'Неподдерживаемый провайдер: {model.provider}'}, status=400)

        print(f"Используем URL: {base_url}")
        print(f"Провайдер модели: '{model.provider}'")
        print(f"Токен: {settings.PROXYAPI_TOKEN[:10]}...")

        # Отправляем запрос к API в зависимости от провайдера
        headers = {
            'Authorization': f'Bearer {settings.PROXYAPI_TOKEN}',
            'Content-Type': 'application/json'
        }

        if model.provider == 'anthropic':
            print("Используем Anthropic API")
            claude_messages = []
            system_content = None

            for msg in api_messages:
                if msg['role'] == 'system':
                    system_content = msg['content']
                else:
                    claude_messages.append(msg)

            payload = {
                'model': model.api_name,
                'messages': claude_messages,
                'max_tokens': 4000
            }

            if system_content:
                payload['system'] = system_content

            endpoint = f'{base_url}/v1/messages'

        elif model.provider == 'google':
            print("Используем Google Gemini API")
            gemini_contents = []

            for msg in api_messages:
                if msg['role'] == 'user':
                    parts = [{"text": msg['content']}]

                    # Добавляем изображение для Gemini
                    if image_id:
                        try:
                            chat_image = ChatImage.objects.get(id=image_id)
                            with open(chat_image.image.path, 'rb') as img_file:
                                image_base64 = base64.b64encode(img_file.read()).decode()
                            parts.append({
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            })
                        except ChatImage.DoesNotExist:
                            pass

                    gemini_contents.append({"parts": parts})
                elif msg['role'] == 'assistant':
                    gemini_contents.append({
                        "role": "model",
                        "parts": [{"text": msg['content']}]
                    })

            payload = {'contents': gemini_contents}
            endpoint = f'{base_url}/v1/models/{model.api_name}:generateContent'

        else:
            print("Используем OpenAI/DeepSeek API")
            payload = {
                'model': model.api_name,
                'messages': api_messages,
                'max_tokens': 4000,
                'temperature': 0.7
            }
            endpoint = f'{base_url}/chat/completions'

        print(f"Отправляем запрос к {endpoint}")

        # Делаем запрос с увеличенным таймаутом и повторными попытками
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=(10, 120)
                )
                break
            except requests.exceptions.Timeout as e:
                print(f"Таймаут на попытке {attempt + 1}: {str(e)}")
                if attempt == max_retries:
                    return JsonResponse(
                        {'error': 'Сервер ИИ не отвечает. Попробуйте позже или выберите другую модель.'}, status=500)
                continue
            except requests.exceptions.RequestException as e:
                print(f"Ошибка запроса на попытке {attempt + 1}: {str(e)}")
                if attempt == max_retries:
                    return JsonResponse({'error': f'Ошибка соединения: {str(e)}'}, status=500)
                continue

        print(f"Статус ответа: {response.status_code}")
        print(f"Содержимое ответа: {response.text[:200]}...")

        if response.status_code == 200:
            result = response.json()

            # Списываем стоимость сообщения
            request.user.charge_for_message()

            # Создаем транзакцию
            if request.user.get_available_messages() >= 0:
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='message',
                    amount=0,
                    description='Бесплатное сообщение с изображением' if image_id else 'Бесплатное сообщение'
                )
            else:
                Transaction.objects.create(
                    user=request.user,
                    transaction_type='message',
                    amount=settings.MESSAGE_PRICE,
                    description='Платное сообщение с изображением' if image_id else 'Платное сообщение'
                )

            if model.provider == 'anthropic':
                ai_response = result['content'][0]['text']
            elif model.provider == 'google':
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content'] and len(
                            candidate['content']['parts']) > 0:
                        ai_response = candidate['content']['parts'][0]['text']
                    else:
                        ai_response = str(candidate.get('content', result))
                else:
                    ai_response = str(result)
            else:
                ai_response = result['choices'][0]['message']['content']

            return JsonResponse({'response': ai_response})
        else:
            error_text = response.text
            print(f"Ошибка API: {error_text}")
            return JsonResponse({'error': f'Ошибка API: {response.status_code}'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный JSON'}, status=400)
    except Exception as e:
        print(f"Исключение: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def upload_image(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Проверяем размер файла (максимум 10MB)
            image_file = request.FILES['image']
            if image_file.size > 10 * 1024 * 1024:
                return JsonResponse({'error': 'Файл слишком большой'}, status=400)

            # Проверяем тип файла
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse({'error': 'Неподдерживаемый тип файла'}, status=400)

            image = ChatImage.objects.create(image=image_file)
            return JsonResponse({
                'success': True,
                'image_id': image.id,
                'image_url': image.image.url
            })
        except Exception as e:
            print(f"Ошибка загрузки изображения: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'No image provided'}, status=400)