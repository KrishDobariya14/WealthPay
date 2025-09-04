from django.shortcuts import render
from django.http import JsonResponse
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
import os 
import google.generativeai as genai
from functools import wraps
# Create your views here.

def home(request):
    """Simple home view to test if server is working"""
    return JsonResponse({
        'message': 'WealthPay Django Backend is running!',
        'status': 'success',
        'available_endpoints': [
            '/api/signup/',
            '/api/login/',
            '/api/transactions/',
            '/api/chatbox/',
            '/admin/'
        ]
    })

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        bank_name=data.get('bank_name')
        account_number = data.get('account_number')
        password = data.get('password')
        print(first_name)
        User.objects.create(First_name=first_name,Last_name=last_name,Account_number=account_number,Email=email,Password=password,Bank_Name=bank_name)
        
        return JsonResponse(data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def login(request):
    if request.method=='POST':
        data = json.loads(request.body)
        email1 = data.get('email')
        password1 = data.get('password')
        e1= serializers.serialize('json', User.objects.filter(Email=email1,Password=password1))
        if e1 is not None:
            return JsonResponse(e1,safe=False)
        else:
            return JsonResponse(e1,safe=False)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

@csrf_exempt
def transaction_view(request):
    if request.method == 'GET':
        # Fetch transactions for the logged-in user
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        email=request.user
        transactions = Transaction.objects.filter(user__icontains={email})
        transaction_list = [
            {
                'transaction_id': transaction.transaction_id,
                'transaction_type': transaction.transaction_type,
                'amount': str(transaction.amount),
                'remark': transaction.remark,
                'created_at': transaction.created_at.isoformat(),
            }
            for transaction in transactions
        ]
        return JsonResponse(transaction_list, safe=False)

    elif request.method == 'POST':
        # Create a new transaction
        data = json.loads(request.body)

        transaction_type = data.get('transaction_type')
        amount = data.get('amount')
        remark = data.get('remark')
        to=data.get('to')
        # Create and save the transaction
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            remark=remark,
            user=data.get('user'), # Set the user from the request
            to=to,
        )
        transaction.save()

        return JsonResponse({
            'transaction_id': transaction.transaction_id,
            'transaction_type': transaction.transaction_type,
            'amount': str(transaction.amount),
            'remark': transaction.remark,
            'created_at': transaction.created_at.isoformat(),
        }, status=201)
    

def transaction_list(request):
    email = request.GET.get('email')
    
    if email:
        transactions = Transaction.objects.filter(user=email)
    else:
        transactions = Transaction.objects.all()
    
    transaction_data = [
        {
            'transaction_id': txn.transaction_id,
            'transaction_type': txn.transaction_type,
            'amount': str(txn.amount),  # convert Decimal to string to avoid serialization issues
            'remark': txn.remark,
            'created_at': txn.created_at,
            'user': txn.user,
            'to': txn.to
        }
        for txn in transactions
    ]
    
    return JsonResponse(transaction_data, safe=False)

GEMINI_API_KEY="AIzaSyCmmmNcaK9fmGTWEIvuuIIokxmto__uSms"


import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def chatbox(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '').strip()

            if not user_input:
                return JsonResponse({'error': 'Input cannot be empty'}, status=400)

            # Check if the input contains investment-related keywords
            investment_keywords = ['investment', 'invest', 'stock', 'mutual fund', 'portfolio', 'savings', 'retirement', 'financial', 'money', 'wealth', 'profit', 'return', 'dividend', 'bond', 'market']
            
            is_investment_related = any(keyword in user_input.lower() for keyword in investment_keywords)
            
            if not is_investment_related:
                return JsonResponse({
                    'response': "I'm an investment specialist. Please ask me questions about investments, stocks, mutual funds, retirement planning, or other financial topics."
                }, status=200)

            try:
                genai.configure(api_key="")

                generation_config = {
                    "temperature": 0,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                }

                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    generation_config=generation_config,
                    system_instruction="you are investment specialist i am going to ask you some investment question in plain text format you have to give me back ans in plain text",
                )

                chat_session = model.start_chat(history=[])
                response = chat_session.send_message(user_input)

                return JsonResponse({'response': response.text}, status=200)

            except Exception as ai_error:
                # Handle API rate limits and other AI service errors
                error_message = str(ai_error)
                
                if "quota" in error_message.lower() or "429" in error_message:
                    # Provide fallback response for rate limit issues
                    fallback_responses = {
                        'investment': "Investment is the act of allocating resources, usually money, with the expectation of generating income or profit. Common investment types include stocks, bonds, mutual funds, and real estate.",
                        'stock': "Stocks represent ownership in a company. When you buy stock, you're purchasing a small piece of that company, called a share. Stock prices can go up or down based on company performance and market conditions.",
                        'mutual fund': "A mutual fund is a type of investment vehicle that pools money from many investors to purchase a diversified portfolio of stocks, bonds, or other securities. This provides diversification and professional management.",
                        'retirement': "Retirement planning involves setting aside money during your working years to support yourself after you stop working. Common retirement accounts include 401(k)s, IRAs, and pension plans.",
                        'savings': "Savings refers to money set aside for future use. It's important to have an emergency fund (3-6 months of expenses) before investing. High-yield savings accounts can help your money grow while keeping it accessible."
                    }
                    
                    # Find the most relevant fallback response
                    for keyword, response in fallback_responses.items():
                        if keyword in user_input.lower():
                            return JsonResponse({
                                'response': f"{response}\n\nNote: I'm currently experiencing high demand. For more detailed advice, please try again later or consult with a financial advisor."
                            }, status=200)
                    
                    # Generic fallback response
                    return JsonResponse({
                        'response': "I'm an investment specialist. I can help you with questions about stocks, mutual funds, retirement planning, and other investment topics. Due to high demand, I'm providing a general response. For specific advice, please try again later or consult with a financial advisor."
                    }, status=200)
                else:
                    # For other AI service errors
                    logger.error(f"AI service error: {error_message}")
                    return JsonResponse({
                        'response': "I'm experiencing technical difficulties with my AI service. Please try again in a few minutes or contact support if the issue persists."
                    }, status=200)

        except Exception as e:
            logger.error(f"Error in chatbox view: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
