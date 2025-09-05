from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib import messages
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from myapp.models import contact_detail
from django.shortcuts import render, redirect, get_object_or_404
from myapp.models import Product,Cart,BillingDetail,Order,OrderItem
from decimal import Decimal
from django.template.loader import render_to_string


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect("cart_page")



@login_required
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.get_total() for item in cart_items)
    shipping = Decimal("3.00") if subtotal > 0 else Decimal("0.00")
    grand_total = subtotal + shipping

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
    })




@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect("cart_page")


@login_required
def update_quantity(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect("cart_page")

def index(request):
    products = Product.objects.all()
    if request.method == "POST":
        s=request.POST.get("search")
        if s:
            products = Product.objects.filter(name__icontains=s)
    return render(request, "index.html", {'products': products})
def shop(request):
    products = Product.objects.all()
    return render(request, "shop.html", {'products': products})
def bestseller(request):
    products = Product.objects.all()
    return render(request, "bestseller.html", {'products': products})
def cart(request):
    return render(request,"cart.html")
def cheackout(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        subtotal = sum(item.get_total() for item in cart_items)
        shipping = 3  # flat shipping or calculate dynamically
        grand_total = subtotal + shipping
    else:
        cart_items = []
        subtotal = 0
        shipping = 0
        grand_total = 0

    return render(request, "cheackout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
    })
def f404(request):
    return render(request,"404.html")
def contact(request):
    if request.method == "POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        project=request.POST.get('project')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        s=contact_detail(name=name,email=email,phone=phone,project=project,subject=subject,message=message)
        s.save()
    return render(request,"contact.html")
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")  # redirect to home
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Send confirmation email
        subject = "Welcome to Electro Store!"
        message = f"Hello {username},\n\nYour account has been created successfully.\n\nLogin and start exploring!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            messages.warning(request, f"Account created but email could not be sent: {e}")

        messages.success(request, "Account created successfully! Please check your email and log in.")
        return redirect("login")

    return render(request, "register.html")


def user_logout(request):
    logout(request)
    return redirect("/")
def myaccount(request):
    return render(request,"myaccount.html")
def firstitems(request):
    return render(request,"firstitems.html")
def seconditems(request):
    return render(request,"seconditems.html")
 # make sure Order/OrderItem models exist

@login_required
def order_confirm(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect("cart_page")

    subtotal = sum(item.get_total() for item in cart_items)
    shipping = Decimal("3.00") if subtotal > 0 else Decimal("0.00")
    grand_total = subtotal + shipping

    if request.method == "POST":
        # Save billing details
        billing = BillingDetail.objects.create(
            user=request.user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            company_name=request.POST.get("company_name"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            country=request.POST.get("country"),
            postcode=request.POST.get("postcode"),
            mobile=request.POST.get("mobile"),
            email=request.POST.get("email"),
            order_notes=request.POST.get("order_notes"),
        )

        # Create Order
        order = Order.objects.create(
            billing=billing,
            user=request.user,
            subtotal=subtotal,
            shipping=shipping,
            grand_total=grand_total,
        )

        # Save order items
        items_copy = []
        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total=item.get_total(),
            )
            items_copy.append({
                'name': item.product.name,
                'model': item.product.id,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'total': float(item.get_total())
            })

        # Store last order id for PDF
        request.session['last_order_id'] = order.id

        # Clear cart
        cart_items.delete()

        # Prepare email
        subject = "Order Confirmation - Electro Store"
        message = f"Hello {request.user.username},\n\nThank you for your order! 🎉\n\n"
        message += f"Billing Details:\nName: {billing.first_name} {billing.last_name}\n"
        message += f"Address: {billing.address}, {billing.city}, {billing.country} - {billing.postcode}\n"
        message += f"Mobile: {billing.mobile}\nEmail: {billing.email}\n\n"
        message += f"Order Details:\nSubtotal: ${subtotal}\nShipping: ${shipping}\nGrand Total: ${grand_total}\n\n"
        message += "Items Ordered:\n"
        for i in items_copy:
            message += f"- {i['name']} (x{i['quantity']}) = ${i['total']}\n"
        if billing.order_notes:
            message += f"\nOrder Notes: {billing.order_notes}\n"
        message += "\nWe will notify you when your order is shipped.\n\nBest regards,\nElectro Store 🌱"

        # Send email safely
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
        except BadHeaderError:
            messages.error(request, "Invalid header found. Email could not be sent.")
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")

        messages.success(request, "✅ Your order has been confirmed! A confirmation email was sent.")

        context = {
            "cart_items": items_copy,
            "subtotal": subtotal,
            "shipping": shipping,
            "grand_total": grand_total,
            "billing": billing,
            "order": order,
        }
        return render(request, "orderconfirm.html", context)

    return redirect("order-confirm")
@login_required
def download_order_pdf(request):
    # Get the last order of the current user
    order = Order.objects.filter(user=request.user).last()
    if not order:
        return HttpResponse("No order found for PDF generation.")

    billing = order.billing
    order_items = OrderItem.objects.filter(order=order)

    # Prepare items for template
    cart_items = [
        {
            'name': item.product.name,
            'model': item.product.id,
            'price': float(item.price),
            'quantity': item.quantity,
            'total': float(item.total)
        } for item in order_items
    ]

    subtotal = float(order.subtotal)
    shipping = float(order.shipping)
    grand_total = float(order.grand_total)

    template_path = "orderconfirm_pdf.html"
    context = {
        "billing": billing,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
        "order": order,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}_invoice.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response
@login_required
def my_order(request):
    # Get all orders for the logged-in user (latest first)
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "myorder.html", context)
