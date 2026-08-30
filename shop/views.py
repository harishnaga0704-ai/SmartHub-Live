from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponse
from django.db.models import Q, Count, Max, Sum, OuterRef, Subquery
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.db import transaction
from django.core.management import call_command
from io import StringIO
import tempfile
import os
from .models import Customer, Product, Order
from .forms import ProductForm, SaleForm


@login_required
def home(request):
    products = Product.objects.all()
    return render(request, "index.html", {
        "products": products
    })


INVENTORY_CATEGORIES = {
    "mobile": "Mobile",
    "laptop": "Laptop",
    "headphones": "Headphones",
    "smart-watch": "Smart Watch",
}


@login_required
@user_passes_test(lambda user: user.is_staff)
def inventory(request, category=None):
    category_label = None
    products = Product.objects.all()
    if category:
        category_label = INVENTORY_CATEGORIES.get(category)
        if not category_label:
            return redirect("inventory")
        products = products.filter(category__iexact=category_label)
    products = products.order_by("-id")
    return render(request, "inventory/inventory.html", {
        "products": products,
        "category_label": category_label,
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def customer_master(request):
    """Show customer-wise purchase history and sales performance."""
    search = request.GET.get("q", "").strip()
    latest_order = Order.objects.filter(customer_profile=OuterRef("pk")).order_by("-created")
    customers = Customer.objects.annotate(
        purchase_count=Count("orders"),
        total_sales=Sum("orders__total", default=0),
        last_purchase=Max("orders__created"),
        last_order_id=Subquery(latest_order.values("id")[:1]),
    ).order_by("-last_purchase")

    if search:
        customers = customers.filter(
            Q(name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )

    now = timezone.now()
    current_start = now - timedelta(days=30)
    previous_start = now - timedelta(days=60)
    current_sales = Order.objects.filter(created__gte=current_start).aggregate(
        total=Sum("total", default=0)
    )["total"]
    previous_sales = Order.objects.filter(
        created__gte=previous_start, created__lt=current_start
    ).aggregate(total=Sum("total", default=0))["total"]
    growth = ((current_sales - previous_sales) / previous_sales * 100) if previous_sales else None

    return render(request, "customers/customer_master.html", {
        "customers": customers,
        "search": search,
        "total_customers": customers.count(),
        "total_sales": Order.objects.aggregate(total=Sum("total", default=0))["total"],
        "current_sales": current_sales,
        "growth": growth,
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def backup_restore(request):
    if request.method == "POST":
        backup_file = request.FILES.get("backup_file")
        if not backup_file or not backup_file.name.lower().endswith(".json"):
            messages.error(request, "Please upload a JSON backup file.")
            return redirect("backup_restore")
        if backup_file.size > 25 * 1024 * 1024:
            messages.error(request, "Backup file must be smaller than 25 MB.")
            return redirect("backup_restore")

        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temporary_file:
                for chunk in backup_file.chunks():
                    temporary_file.write(chunk)
                temporary_path = temporary_file.name
            with transaction.atomic():
                call_command("loaddata", temporary_path, verbosity=0)
            messages.success(request, "Database backup restored successfully.")
        except Exception as error:
            messages.error(request, f"Restore failed: {error}")
        finally:
            if temporary_path:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass
        return redirect("backup_restore")

    return render(request, "backup_restore.html")


@login_required
@user_passes_test(lambda user: user.is_staff)
def download_backup(request):
    output = StringIO()
    call_command(
        "dumpdata",
        "shop",
        "auth.user",
        exclude=["contenttypes", "auth.permission", "sessions"],
        natural_foreign=True,
        natural_primary=True,
        indent=2,
        stdout=output,
    )
    response = HttpResponse(output.getvalue(), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="smartsy-backup.json"'
    return response


@login_required
def invoice(request, id):
    order = get_object_or_404(Order.objects.select_related("product"), id=id)
    if not request.user.is_staff and order.customer_id != request.user.id:
        return redirect("index")
    return render(request, "customers/invoice.html", {"order": order})


@login_required
def invoice_pdf(request, id):
    """Create a downloadable PDF copy of an invoice."""
    order = get_object_or_404(Order.objects.select_related("product"), id=id)
    if not request.user.is_staff and order.customer_id != request.user.id:
        return redirect("index")

    # Minimal standards-compliant PDF writer: avoids an external package dependency.
    def escape_pdf(text):
        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")

    invoice_lines = [
        ("SMARTSY Electronics", 18),
        (f"SALES INVOICE  #{order.id:05d}", 12),
        (f"Invoice Date: {order.created.strftime('%d %b %Y')}", 10),
        ("", 10), ("FROM", 10), ("SMARTSY Electronics", 10),
        ("SMARTSY Online Store | support@smartsy.com | India", 10),
        ("", 10), ("TO", 10), (order.customer_name, 10), (order.email, 10), (order.phone, 10),
        *[(address_line, 10) for address_line in order.address.splitlines() or [order.address]],
        ("", 10), (f"Product: {order.product.name}", 11), (f"Category: {order.product.category}", 10),
        (f"Quantity: {order.quantity}", 10), (f"Payment method: {order.payment_method}", 10),
        (f"Grand Total: Rs. {order.total:.2f}", 13), ("", 10),
        ("Customer Signature                                      Authorised Signature", 9),
    ]
    y = 800
    commands = []
    for text, font_size in invoice_lines:
        commands.append(f"BT /F1 {font_size} Tf 45 {y} Td ({escape_pdf(text)}) Tj ET")
        y -= font_size + 7
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode())
    response = HttpResponse(bytes(pdf), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="SMARTSY-Invoice-{order.id:05d}.pdf"'
    return response


@login_required
@user_passes_test(lambda user: user.is_staff)
def add_sale(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            if product.stock < quantity:
                form.add_error("quantity", f"Only {product.stock} item(s) available in stock.")
            else:
                unit_price = product.offer_price if product.offer_price is not None else product.price
                with transaction.atomic():
                    order = form.save(commit=False)
                    customer_profile, _ = Customer.objects.update_or_create(
                        email=form.cleaned_data["email"],
                        phone=form.cleaned_data["phone"],
                        defaults={
                            "name": form.cleaned_data["customer_name"],
                            "address": form.cleaned_data["address"],
                            "user": request.user,
                        },
                    )
                    order.total = unit_price * quantity
                    order.status = "Completed"
                    order.customer = request.user
                    order.customer_profile = customer_profile
                    order.save()
                    product.stock -= quantity
                    product.save(update_fields=["stock"])
                messages.success(request, "Invoice created successfully.")
                return redirect("invoice", id=order.id)
    else:
        form = SaleForm()

    return render(request, "customers/add_sale.html", {"form": form})


@login_required
@user_passes_test(lambda user: user.is_staff)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"{product.name} was added to inventory.")
            return redirect("inventory")
    else:
        form = ProductForm(initial={"category": request.GET.get("category", "")})

    return render(request, "inventory/add_product.html", {
        "form": form
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"{product.name} was updated.")
            return redirect("inventory")
    else:
        form = ProductForm(instance=product)

    return render(request, "inventory/edit_product.html", {
        "form": form,
        "product": product
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(request, f"{product_name} was removed from inventory.")
        return redirect("inventory")

    return render(request, "inventory/delete_product.html", {
        "product": product
    })


@login_required
def product_detail(request, id):
    product = get_object_or_404(Product.objects.prefetch_related("detail_images"), id=id)
    return render(request, "product_detail.html", {
        "product": product
    })


@login_required
def category_products(request, category):
    products = Product.objects.filter(category__iexact=category)
    return render(request, "products.html", {
        "products": products,
        "category": category
    })


@login_required
def mobile(request):
    db_products = Product.objects.filter(Q(category__iexact="mobile") | Q(category__iexact="mobiles"))
    for p in db_products:
        if p.offer_price and p.price > p.offer_price:
            p.discount_percent = int(((p.price - p.offer_price) / p.price) * 100)
    return render(request, "mobile.html", {"db_products": db_products})


@login_required
def laptop(request):
    db_products = Product.objects.filter(Q(category__iexact="laptop") | Q(category__iexact="laptops"))
    for p in db_products:
        if p.offer_price and p.price > p.offer_price:
            p.discount_percent = int(((p.price - p.offer_price) / p.price) * 100)
    return render(request, "laptops.html", {"db_products": db_products})


@login_required
def headphones(request):
    db_products = Product.objects.filter(Q(category__iexact="headphone") | Q(category__iexact="headphones"))
    for p in db_products:
        if p.offer_price and p.price > p.offer_price:
            p.discount_percent = int(((p.price - p.offer_price) / p.price) * 100)
    return render(request, "headphones.html", {"db_products": db_products})


@login_required
def smart(request):
    db_products = Product.objects.filter(
        Q(category__iexact="smart watch")
        | Q(category__iexact="smart watches")
        | Q(category__iexact="smart")
    )
    for product in db_products:
        if product.offer_price and product.price > product.offer_price:
            product.discount_percent = int(((product.price - product.offer_price) / product.price) * 100)
    return render(request, "smart.html", {"db_products": db_products})


@login_required
def checkout(request):
    return render(request, "checkout.html")


@login_required
def cart(request):
    return render(request, "Cart.html")


@login_required
def place_order(request):
    """Create completed orders from the customer's browser cart."""
    if request.method != "POST":
        return JsonResponse({"error": "POST requests only."}, status=405)

    try:
        payload = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid order data."}, status=400)

    customer_name = str(payload.get("customer_name", "")).strip()
    email = str(payload.get("email", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    address = str(payload.get("address", "")).strip()
    payment_method = str(payload.get("payment_method", "")).strip().upper()
    cart_items = payload.get("items", [])

    if not all((customer_name, email, phone, address)):
        return JsonResponse({"error": "Please enter all customer details."}, status=400)
    if payment_method not in {"GPAY", "COD"}:
        return JsonResponse({"error": "Please select GPay or Cash on Delivery."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    if not isinstance(cart_items, list) or not cart_items:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    try:
        with transaction.atomic():
            customer_profile, _ = Customer.objects.update_or_create(
                email=email,
                phone=phone,
                defaults={
                    "name": customer_name,
                    "address": address,
                    "user": request.user,
                },
            )
            orders = []
            for item in cart_items:
                if not isinstance(item, dict):
                    raise ValueError("Invalid cart item.")
                product_id = item.get("product_id")
                quantity = int(item.get("quantity", 0))
                if quantity < 1:
                    raise ValueError("Each cart item needs a valid quantity.")

                products = Product.objects.select_for_update()
                if product_id:
                    product = products.get(id=product_id)
                else:
                    product = products.filter(name__iexact=str(item.get("name", "")).strip()).first()
                    if product is None:
                        raise ValueError("A cart product is no longer available.")
                if product.stock < quantity:
                    raise ValueError(f"Only {product.stock} item(s) of {product.name} are available.")

                unit_price = product.offer_price if product.offer_price is not None else product.price
                orders.append(Order(
                    customer_profile=customer_profile,
                    customer=request.user,
                    customer_name=customer_name,
                    email=email,
                    phone=phone,
                    address=address,
                    product=product,
                    quantity=quantity,
                    total=unit_price * quantity,
                    payment_method=payment_method,
                    status="Completed",
                ))
                product.stock -= quantity
                product.save(update_fields=["stock"])

            Order.objects.bulk_create(orders)
    except (Product.DoesNotExist, TypeError, ValueError) as error:
        return JsonResponse({"error": str(error) or "Unable to place the order."}, status=400)

    invoice_url = reverse("invoice", args=[orders[0].id]) + "?placed=1"
    return JsonResponse({
        "message": "Order placed successfully.",
        "order_count": len(orders),
        "invoice_url": invoice_url,
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def order_notifications(request):
    """Return orders that have not yet been opened by an administrator."""
    orders = Order.objects.filter(is_seen=False).order_by("-created")[:10]
    return JsonResponse({
        "orders": [
            {
                "id": order.id,
                "customer_name": order.customer_name,
                "total": str(order.total),
            }
            for order in orders
        ]
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def order_notification(request, id):
    """Mark an order notification as seen, then open its invoice."""
    order = get_object_or_404(Order, id=id)
    if not order.is_seen:
        order.is_seen = True
        order.save(update_fields=["is_seen"])
    return redirect("invoice", id=order.id)


@login_required
def contact(request):
    return render(request, "contact.html")


# ---- AUTH VIEWS ----

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or "index"
            return redirect(next_url)

    return render(request, "login.html", {"form": form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")

    return render(request, "signup.html", {"form": form})
