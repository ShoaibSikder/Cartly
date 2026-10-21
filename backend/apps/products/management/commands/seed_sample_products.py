from decimal import Decimal

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from apps.products.models import Product


SAMPLE_PRODUCTS = (
    {
        "name": "Stoneware Coffee Set",
        "slug": "stoneware-coffee-set",
        "description": (
            "A pair of speckled stoneware mugs with a warm, comfortable shape "
            "for slow mornings and everyday coffee."
        ),
        "price": Decimal("1450.00"),
        "stock": 18,
        "category": "Home & Living",
        "image": "products/stoneware-coffee-set.png",
    },
    {
        "name": "Linen Cushion Cover",
        "slug": "linen-cushion-cover",
        "description": (
            "A soft, textured linen-blend cushion cover in a calm natural tone. "
            "Includes a concealed zip and fits a standard 45 cm cushion."
        ),
        "price": Decimal("890.00"),
        "stock": 24,
        "category": "Home & Living",
        "image": "products/linen-cushion-cover.png",
    },
    {
        "name": "Arc Desk Lamp",
        "slug": "arc-desk-lamp",
        "description": (
            "A compact adjustable desk lamp with a weighted base and warm LED "
            "light for focused work or reading."
        ),
        "price": Decimal("2850.00"),
        "stock": 12,
        "category": "Electronics",
        "image": "products/arc-desk-lamp.png",
    },
    {
        "name": "Wireless Studio Headphones",
        "slug": "wireless-studio-headphones",
        "description": (
            "Comfortable over-ear wireless headphones with cushioned ear cups, "
            "simple controls, and a fold-flat design."
        ),
        "price": Decimal("4250.00"),
        "stock": 9,
        "category": "Electronics",
        "image": "products/wireless-studio-headphones.png",
    },
    {
        "name": "Everyday Canvas Tote",
        "slug": "everyday-canvas-tote",
        "description": (
            "A sturdy cotton-canvas carryall with reinforced handles and room "
            "for daily essentials, books, or groceries."
        ),
        "price": Decimal("720.00"),
        "stock": 30,
        "category": "Accessories",
        "image": "products/everyday-canvas-tote.png",
    },
    {
        "name": "Insulated Steel Bottle",
        "slug": "insulated-steel-bottle",
        "description": (
            "A reusable double-wall stainless steel bottle with a leak-resistant "
            "lid, sized for a bag or desk."
        ),
        "price": Decimal("1180.00"),
        "stock": 20,
        "category": "Accessories",
        "image": "products/insulated-steel-bottle.png",
    },
)


class Command(BaseCommand):
    help = "Add sample products and update their product image files."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        existing_count = 0

        for product_data in SAMPLE_PRODUCTS:
            image_name = product_data["image"]
            if not default_storage.exists(image_name):
                raise CommandError(f"Product image does not exist: {image_name}")

            product, created = Product.objects.get_or_create(
                slug=product_data["slug"],
                defaults=product_data,
            )
            if created:
                created_count += 1
            elif product.image.name != image_name:
                product.image = image_name
                product.save(update_fields=["image", "updated_at"])
                updated_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sample catalog ready: {created_count} added, "
                f"{updated_count} images updated, "
                f"{existing_count} already current."
            )
        )
