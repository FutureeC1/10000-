from database.repositories import OrderRepository, ProductRepository, UserRepository, ShopRepository

def get_superadmin_stats() -> dict:
    """Статистика для супер-администратора (все магазины)."""
    return {
        "shops_count": ShopRepository.get_shops_count(),
        "products_count": ProductRepository.get_all_products_count(),
        "orders_count": OrderRepository.get_all_orders_count(),
        "completed_orders_count": OrderRepository.get_all_completed_orders_count(),
        "clients_count": UserRepository.get_users_count()
    }

def get_shop_owner_stats(shop_id: int) -> dict:
    """Статистика для конкретного магазина (владелец магазина)."""
    return {
        "products_count": ProductRepository.get_products_count_by_shop(shop_id),
        "orders_count": OrderRepository.get_orders_count_by_shop(shop_id),
        "completed_orders_count": OrderRepository.get_completed_orders_count_by_shop(shop_id)
    }
