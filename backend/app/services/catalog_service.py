from app.models.service_item import ServiceItem


CATEGORY_TEMPLATES = {
    "tailor": [
        {"name": "Blouse stitching", "price_min": 150, "price_max": 300, "duration_mins": 45},
        {"name": "Shirt alteration", "price_min": 80, "price_max": 150, "duration_mins": 25},
        {"name": "Saree fall stitching", "price_min": 50, "price_max": 120, "duration_mins": 20},
        {"name": "Home pickup", "supports_home_visit": True},
    ],
    "salon": [
        {"name": "Men's haircut", "price_min": 200, "price_max": 350, "duration_mins": 30},
        {"name": "Beard trim", "price_min": 80, "price_max": 150, "duration_mins": 15},
        {"name": "Facial", "price_min": 500, "price_max": 900, "duration_mins": 45},
        {"name": "Home visit", "supports_home_visit": True},
    ],
    "kirana": [
        {"name": "Grocery delivery", "supports_home_visit": True},
        {"name": "Monthly staples packing"},
        {"name": "WhatsApp ordering"},
    ],
}


def seed_service_template(db, shop):
    template = CATEGORY_TEMPLATES.get(shop.category.lower(), [])
    existing_names = {item.name for item in shop.service_items} if getattr(shop, "service_items", None) else set()
    created = []
    for entry in template:
        if entry["name"] in existing_names:
            continue
        service = ServiceItem(
            shop_id=shop.id,
            name=entry["name"],
            price_min=entry.get("price_min"),
            price_max=entry.get("price_max"),
            duration_mins=entry.get("duration_mins"),
            supports_home_visit=entry.get("supports_home_visit", False),
        )
        db.add(service)
        created.append(service)
    return created
