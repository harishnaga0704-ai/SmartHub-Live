"""Download catalogue images already referenced by the product pages.

Run from the project root with ``python shop/sync_catalogue_images.py``.
Only successfully downloaded, valid image files replace a product's existing image.
"""

import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from PIL import Image

from shop.models import Product


TEMPLATES = [
    ROOT / "templates" / name
    for name in ("products.html", "mobile.html", "laptops.html", "headphones.html")
]
OUTPUT_DIR = Path(settings.MEDIA_ROOT) / "products" / "catalogue"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def normalise(name):
    return " ".join(name.casefold().split())


def product_image_urls():
    """Read the name/image pairs from the existing product-card templates."""
    images = {}
    card_pattern = re.compile(
        r"addToCart\(\s*'([^']+)'\s*,\s*[^,]+\s*,\s*'([^']+)'", re.S
    )
    object_pattern = re.compile(
        r'name\s*:\s*"([^"]+)"[\s\S]{0,500}?image\s*:\s*"([^"]+)"', re.S
    )
    for template in TEMPLATES:
        text = template.read_text(encoding="utf-8")
        for name, image_url in card_pattern.findall(text) + object_pattern.findall(text):
            if image_url.startswith("https://"):
                images[normalise(name)] = image_url
    return images


def download(product, image_url):
    target = OUTPUT_DIR / f"exact-product-{product.id}.jpg"
    try:
        request = Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get_content_type()
            data = response.read()
        if not content_type.startswith("image/") or not data:
            raise ValueError("source did not return an image")
        target.write_bytes(data)
        with Image.open(target) as image:
            image.verify()
        return product, target
    except Exception as error:
        target.unlink(missing_ok=True)
        return product, error


def main():
    image_urls = product_image_urls()
    work = [
        (product, image_urls[normalise(product.name)])
        for product in Product.objects.all()
        if normalise(product.name) in image_urls
    ]
    updated = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(download, product, url) for product, url in work]
        for future in as_completed(futures):
            product, result = future.result()
            if isinstance(result, Path):
                product.image = f"products/catalogue/{result.name}"
                product.save(update_fields=["image"])
                updated += 1
            else:
                print(f"Kept existing image for {product.name}: {result}")
    print(f"Updated {updated} product images from exact catalogue-card sources.")


if __name__ == "__main__":
    main()
