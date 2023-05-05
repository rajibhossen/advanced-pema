#!/usr/bin/env bash
kubectl exec ts-auth-mongo-84bd8557b5-25vbn -- mongo ts-auth-mongo --eval "db.user.remove({'roles':'ROLE_USER'})"
kubectl exec ts-assurance-mongo-5bddf4469f-b6vjh -- mongo ts --eval "db.assurance.remove({})"
kubectl exec ts-consign-mongo-69bdccb6f9-wn25d -- mongo ts --eval "db.consign_record.remove({})"
kubectl exec ts-contacts-mongo-7d5fcdc5ff-drkz4 -- mongo ts --eval "db.contacts.remove({})"
kubectl exec ts-food-mongo-56ddfc56f-hrsnc -- mongo ts --eval "db.foodorder.remove({})"
kubectl exec ts-order-mongo-7cd85f8d5b-r7ltn -- mongo ts --eval "db.orders.remove({})"
kubectl exec ts-user-mongo-76c774fcbc-vp4vd -- mongo ts-user-mongo --eval "db.user.remove({})"
