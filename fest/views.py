import logging
from .models import Payment
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .mpesa_api import stk_push
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from fest.forms import ContactForm, RegisterForm
from fest.models import Contact
import json


# Home page view
def index(request):
    return render(request, 'index.html')


def speaker_details(request):
    return render(request, 'speaker-details.html')


def starter_page(request):
    return render(request, 'starter-page.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully sent your message')
            return redirect('index')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


@login_required
def customerlist(request):
    data = Contact.objects.all()
    return render(request, 'customerlist.html', {'data': data})


def editcustomer(request, id):
    customer = get_object_or_404(Contact, id=id)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customerlist')
    else:
        form = ContactForm(instance=customer)
    return render(request, 'editcustomer.html', {'form': form, 'customer': customer})


def deletecustomer(request, id):
    customer = get_object_or_404(Contact, id=id)
    customer.delete()
    messages.success(request, "Customer deleted successfully")
    return redirect('customerlist')


# User Registration View
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return HttpResponse("Passwords do not match", status=400)

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken!"})

        user = User.objects.create(username=username, email=email)
        user.set_password(password1)
        user.save()

        login(request, user)
        return redirect("index")

    return render(request, "register.html")


# User Login View
def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'login.html', {'error': error_message})


# User Logout View
def logout_view(request):
    logout(request)
    return redirect("login")


# Render the buy ticket page
def buy_ticket(request):
    return render(request, "buy_ticket.html")

# STK Push request



logger = logging.getLogger(__name__)  # Add logging to track errors


@login_required
def stk_push_request(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone")
        amount = request.POST.get("amount")

        if not phone_number or not amount:
            return JsonResponse({"error": "Phone number and amount are required"}, status=400)

        try:
            amount = int(amount)

            # Ensure phone number format is correct
            if phone_number.startswith("07"):
                phone_number = "254" + phone_number[1:]

            response = stk_push(phone_number, amount)  # Call M-Pesa API

            if "CheckoutRequestID" in response:
                transaction_id = response["CheckoutRequestID"]

                # Save payment details
                Payment.objects.create(
                    user=request.user,
                    phone_number=phone_number,
                    amount=amount,
                    transaction_id=transaction_id,
                    status="Pending"
                )
                return JsonResponse({"success": "STK Push sent to your phone.", "transaction_id": transaction_id})

            # Log error response
            logger.error(f"STK Push Failed: {response}")
            return JsonResponse({"error": f"Failed to initiate payment: {response}"}, status=500)

        except Exception as e:
            logger.error(f"Error in stk_push_request: {str(e)}")
            return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# M-Pesa Callback Handling

logger = logging.getLogger(__name__)

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logger.info(f"MPESA CALLBACK RECEIVED: {json.dumps(data, indent=4)}")

            checkout_request_id = data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
            result_code = data.get("Body", {}).get("stkCallback", {}).get("ResultCode")

            payment = Payment.objects.filter(transaction_id=checkout_request_id).first()

            if payment:
                payment.status = "Success" if result_code == 0 else "Failed"
                payment.save()
                return JsonResponse({"success": "Payment updated"})

            return JsonResponse({"error": "Transaction not found"}, status=404)

        except Exception as e:
            logger.error(f"MPESA CALLBACK ERROR: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

# Payment History View
@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, "payment_history.html", {"payments": payments})
