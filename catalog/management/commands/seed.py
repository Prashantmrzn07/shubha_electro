from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from catalog.models import Brand, Category, Product

User = get_user_model()

CATEGORIES = [
    ("Televisions", "LED, QLED and smart TVs for living rooms."),
    ("Refrigerators", "Single door, double door and side-by-side refrigerators."),
    ("Washing Machines", "Front load, top load and washer-dryer combos."),
    ("Air Conditioners", "Split and inverter ACs for home cooling."),
    ("Microwaves", "Solo, grill and convection microwave ovens."),
    ("Other Home Appliances", "Fans, irons, vacuum cleaners and more."),
]

BRANDS = ["Samsung", "LG", "Sony", "Whirlpool", "Haier", "Panasonic", "Godrej"]

PRODUCTS = [
    {
        "category": "Televisions",
        "brand": "Samsung",
        "name": "55-inch Crystal UHD 4K Smart TV",
        "price": "89990.00",
        "stock": 12,
        "warranty": "2 years",
        "description": "A bright 4K smart TV with streaming apps, HDR and slim bezels for living-room viewing.",
        "specifications": "Screen: 55 inch 4K UHD\nHDR: HDR10+\nOS: Tizen\nHDMI: 3 ports\nRefresh: 60 Hz",
    },
    {
        "category": "Televisions",
        "brand": "Sony",
        "name": "43-inch Bravia Full HD LED TV",
        "price": "54990.00",
        "stock": 8,
        "warranty": "2 years",
        "description": "Reliable Full HD TV with X-Reality picture processing and multiple HDMI inputs.",
        "specifications": "Screen: 43 inch Full HD\nProcessor: X-Reality PRO\nHDMI: 2 ports\nUSB: 2 ports",
    },
    {
        "category": "Refrigerators",
        "brand": "LG",
        "name": "260L Double Door Refrigerator",
        "price": "64990.00",
        "stock": 6,
        "warranty": "1 year + 10 years compressor",
        "description": "Frost-free double door fridge with inverter compressor for lower energy use.",
        "specifications": "Capacity: 260 L\nType: Frost free double door\nInverter: Yes\nShelves: Toughened glass",
    },
    {
        "category": "Refrigerators",
        "brand": "Whirlpool",
        "name": "190L Single Door Refrigerator",
        "price": "24990.00",
        "stock": 15,
        "warranty": "1 year",
        "description": "Compact single door fridge suited for small kitchens and hostels.",
        "specifications": "Capacity: 190 L\nType: Direct cool single door\nStabilizer: Built-in\nColor: Grey",
    },
    {
        "category": "Washing Machines",
        "brand": "Samsung",
        "name": "7kg Front Load Washing Machine",
        "price": "42990.00",
        "stock": 4,
        "warranty": "2 years",
        "description": "Front load washer with multiple wash programs and a digital inverter motor.",
        "specifications": "Capacity: 7 kg\nType: Fully automatic front load\nRPM: 1200\nEnergy: 5 star",
    },
    {
        "category": "Washing Machines",
        "brand": "LG",
        "name": "8kg Top Load Washing Machine",
        "price": "32990.00",
        "stock": 9,
        "warranty": "2 years",
        "description": "Top load washer with smart motion wash and punch+3 technology.",
        "specifications": "Capacity: 8 kg\nType: Fully automatic top load\nInverter: Yes\nPrograms: 10",
    },
    {
        "category": "Air Conditioners",
        "brand": "Haier",
        "name": "1.5 Ton Inverter Split AC",
        "price": "72990.00",
        "stock": 5,
        "warranty": "1 year + 5 years compressor",
        "description": "Energy-efficient inverter split AC for medium rooms.",
        "specifications": "Capacity: 1.5 Ton\nType: Split inverter\nCopper coil: Yes\nStar rating: 3 star",
    },
    {
        "category": "Air Conditioners",
        "brand": "Panasonic",
        "name": "1 Ton Split AC",
        "price": "58990.00",
        "stock": 3,
        "warranty": "1 year",
        "description": "Quiet 1-ton split AC for bedrooms with dust filter.",
        "specifications": "Capacity: 1 Ton\nType: Split\nFilter: PM 2.5\nRefrigerant: R32",
    },
    {
        "category": "Microwaves",
        "brand": "Samsung",
        "name": "28L Convection Microwave Oven",
        "price": "18990.00",
        "stock": 11,
        "warranty": "1 year",
        "description": "Convection microwave for baking, grilling and everyday heating.",
        "specifications": "Capacity: 28 L\nType: Convection\nPower: 900 W\nPresets: 30 auto cook",
    },
    {
        "category": "Microwaves",
        "brand": "LG",
        "name": "20L Solo Microwave Oven",
        "price": "9990.00",
        "stock": 18,
        "warranty": "1 year",
        "description": "Solo microwave for quick heating and defrosting.",
        "specifications": "Capacity: 20 L\nType: Solo\nPower: 700 W\nControl: Tact",
    },
    {
        "category": "Other Home Appliances",
        "brand": "Panasonic",
        "name": "1600W Steam Iron",
        "price": "3490.00",
        "stock": 2,
        "warranty": "1 year",
        "description": "Steam iron with ceramic soleplate for everyday clothes.",
        "specifications": "Power: 1600 W\nSoleplate: Ceramic\nSteam: Vertical steam\nTank: 300 ml",
    },
    {
        "category": "Other Home Appliances",
        "brand": "Godrej",
        "name": "Cyclonic Vacuum Cleaner",
        "price": "7990.00",
        "stock": 7,
        "warranty": "1 year",
        "description": "Bagless vacuum cleaner for floors and upholstery.",
        "specifications": "Type: Bagless cyclonic\nPower: 1400 W\nCapacity: 2 L\nAccessories: 3 nozzles",
    },
]


class Command(BaseCommand):
    help = "Load demo categories, brands, products, admin and customer users."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="prashantmhrh77@gail.com",
            defaults={
                "email": "prashantmhrh77@gail.com",
                "first_name": "Shop",
                "last_name": "Admin",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Prashant6969")
            admin.save()
            self.stdout.write("Created admin user (prashantmhrh77@gail.com / Prashant6969)")
        else:
            changed = False
            if admin.email != "prashantmhrh77@gail.com":
                admin.email = "prashantmhrh77@gail.com"
                changed = True
            if admin.role != User.ROLE_ADMIN or not admin.is_staff:
                admin.role = User.ROLE_ADMIN
                admin.is_staff = True
                changed = True
            if changed:
                admin.save()
            self.stdout.write("Admin user already exists")

        admin_alt, created_alt = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "System",
                "last_name": "Admin",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created_alt:
            admin_alt.set_password("admin123")
            admin_alt.save()
            self.stdout.write("Created admin user (admin / admin123)")

        customer, created = User.objects.get_or_create(
            username="prashant",
            defaults={
                "email": "prashant@example.com",
                "first_name": "Prashant",
                "last_name": "Maharjan",
                "role": User.ROLE_CUSTOMER,
                "phone": "9800000000",
                "address": "Kist College area, Kathmandu",
            },
        )
        if created:
            customer.set_password("prashant123")
            customer.save()
            self.stdout.write("Created customer (prashant / prashant123)")

        categories = {}
        for name, description in CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name, defaults={"description": description})
            categories[name] = category
        brands = {}
        for name in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=name)
            brands[name] = brand

        created_count = 0
        for item in PRODUCTS:
            _, was_created = Product.objects.get_or_create(
                name=item["name"],
                defaults={
                    "category": categories[item["category"]],
                    "brand": brands[item["brand"]],
                    "price": item["price"],
                    "stock": item["stock"],
                    "warranty": item["warranty"],
                    "description": item["description"],
                    "specifications": item["specifications"],
                    "is_active": True,
                },
            )
            if was_created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Products added: {created_count}"))
