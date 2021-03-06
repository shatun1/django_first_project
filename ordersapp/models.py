from django.conf import settings
from django.db import models

from mainapp.models import Product


class OrderItemQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for object in self:
            object.product.quantity += object.quantity
            object.product.save()
        super(OrderItemQuerySet, self).delete(*args, **kwargs)


class Order(models.Model):
    objects = OrderItemQuerySet.as_manager()

    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'

    ORDERS_STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в обработку'),
        (PAID, 'оплачен'),
        (PROCEEDED, 'обрабатывается'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        verbose_name='создан',
        auto_now_add=True,
    )
    update = models.DateTimeField(
        verbose_name='обновлен',
        auto_now=True,
    )
    status = models.CharField(
        verbose_name='статус',
        max_length=3,
        choices=ORDERS_STATUS_CHOICES,
        default=FORMING,
    )
    is_active = models.BooleanField(
        verbose_name='активен',
        default=True,
        db_index=True
    )

    def __str__(self):
        return f'Текущий заказ: {self.id}'

    def get_summary(self):
        items = self.orderitems.select_related()
        return {
            'total_cost': sum(list(map(lambda x: x.quantity * x.product.price, items))),
            'total_quantity': sum(list(map(lambda x: x.quantity, items))),
        }

    def get_total_quantity(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity, items)))

    def get_product_type_quantity(self):
        items = self.orderitems.select_related()
        return len(items)

    def get_total_cost(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity * x.product.price, items)))

    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="orderitems",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        on_delete=models.CASCADE,
    )

    # status = models.ForeignKey(
    #     status
    # )

    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=0,
    )

    def get_product_cost(self):
        return self.product.price * self.quantity

    # def delete(self):
    #     self.product.quantity += self.quantity
    #     self.product.save()
    #     super(self.__class__, self).delete()
