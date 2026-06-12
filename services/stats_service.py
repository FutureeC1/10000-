from database.repositories import OrderRepository, ProductRepository, UserRepository

def get_admin_stats() -> dict:
    return {
        "orders_count": OrderRepository.get_orders_count(),
        "clients_count": UserRepository.get_users_count(),
        "products_count": ProductRepository.get_products_count(),
        "completed_orders_count": OrderRepository.get_completed_orders_count()
    }
