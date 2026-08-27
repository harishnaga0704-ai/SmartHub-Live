from django import forms
from .models import Product, Order


CATEGORY_CHOICES = [
    ('Mobile', 'Mobile'),
    ('Laptop', 'Laptop'),
    ('Headphones', 'Headphones'),
    ('Smart Watch', 'Smart Watch'),
]


class ProductForm(forms.ModelForm):

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'brand',
            'price',
            'offer_price',
            'stock',
            'rating',
            'description',
            'specifications',
            'image',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'MRP'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Offer price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock count'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0-5', 'step': '0.1', 'min': '0', 'max': '5'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Display: 6.7 inch\nBattery: 5000 mAh\nWarranty: 1 year'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        offer_price = cleaned_data.get('offer_price')
        stock = cleaned_data.get('stock')

        if price is not None and price < 0:
            self.add_error('price', 'Price cannot be negative.')
        if offer_price is not None and offer_price < 0:
            self.add_error('offer_price', 'Offer price cannot be negative.')
        if price is not None and offer_price is not None and offer_price > price:
            self.add_error('offer_price', 'Offer price cannot be higher than the price.')
        if stock is not None and stock < 0:
            self.add_error('stock', 'Stock cannot be negative.')

        return cleaned_data


class SaleForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "email", "phone", "address", "product", "quantity", "payment_method"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Customer name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Customer email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Billing address"}),
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "payment_method": forms.Select(
                choices=[("GPAY", "GPay"), ("COD", "Cash on Delivery (COD)")],
                attrs={"class": "form-select"},
            ),
        }
