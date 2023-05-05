kubectl exec -n sock-shop carts-db-6d7546f9f9-8jl4q -- mongo data --eval "db.cart.remove({})"
kubectl exec -n sock-shop carts-db-6d7546f9f9-8jl4q -- mongo data --eval "db.item.remove({})"
kubectl exec -n sock-shop orders-db-5bf887f4c-v6h8m -- mongo data --eval "db.customerOrder.remove({})"
