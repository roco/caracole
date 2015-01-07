#!/usr/bin/python
# -*- coding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

# A user belongs can belong to several networks, through one subgroup per network.
# They might also be staff of several subgroups,
# and staff of several networks.
# Symmetrically, subgroups and networks can each have several staff.


class Plural(models.Model):
    """Remember the plural of product and unit names.
    Django supports plurals for words occurring verbatim in templates,
    but not for words coming from the DB."""
    singular = models.CharField(max_length=64)
    plural = models.CharField(max_length=64)

    def __unicode__(self):
        return "%s/%s" % (self.singular, self.plural)


# TODO: implement a cache?
def plural(noun, n=None):
    """Tries to retrieve of guess the plural of a singular French word.
    It would be great to hook this up to a (possibly online) dictionary.

    :param noun: the French noun to try and pluralize
    :param n: number of stuff (optional): don't pluralize if |n| < 2.
    :return: pluralized noun."""

    if n is not None and -2 < n < 2:
        return noun  # No need to pluralize
    try:
        return Plural.objects.get(singular=noun).plural
    except Plural.DoesNotExist:
        if noun[-1] == 's' or noun[-1] == 'x':
            return noun  # Probably invariant
        elif noun[-2:] == 'al':
            return noun[:-2] + 'aux'
        elif noun[-3:] == 'eau':
            return noun + 'x'
        else:
            return noun + 's'  # probably a regular plural


def articulate(noun, n=1):
    """Prepend an appropriate French article to a word.
    Caveat: doesn't handle 'y' nor 'h' correctly.

    :param noun: the noun in need of an article
    :param n: quantity of the noun, to determine whether it needs to be pluralized
    :return: the noun with an indefinite article, possibly in the plural form."""

    if 'aeiou'.count(noun[0].lower()):
        return "d'" + plural(noun, n)
    else:
        return "de " + plural(noun, n)


class Network(models.Model):
    """One distribution network. Deliveries are passed for a whole network,
    then broken up into subgroups.
    The network has staff users, in charge of allowing, forbidding and pricing products
    in commands.

    Staff users are often also users allowed to order, but this isn't mandatory.
    Regular users are not stored diretly in the network: they're stored in the network's
    subgroup they belong to."""

    name = models.CharField(max_length=64)
    staff = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name


class Subgroup(models.Model):
    """Subgroup of a network. Each subgroup has a set of regular users, and a set of staff
    users. Staff users are allowed to modify the commands of their group users' purchases,
    even if the delivery is closed (but not if it's already delivered). Staff users are
    typically also regular users, but this is not mandatory.

    Each subgroup has an 'Extra' user; staff users can order on behalf of the extra user,
    so that the subgroup's order sums up to entire boxes, if network staff wishes so.
    Extra users are allowed to order a negative quantity of products."""

    name = models.CharField(max_length=64)
    network = models.ForeignKey(Network)
    extra_user = models.ForeignKey(User, null=True, blank=True, related_name='+')
    # Users might only be staff of one subgroup per network
    staff = models.ManyToManyField(User, related_name='staff_of')
    users = models.ManyToManyField(User, related_name='user_of')

    def __unicode__(self):
        return "%s/%s" % (self.network.name, self.name)

    # TODO: override create() so that the extra user is automatically created;
    # TODO: delete extra_user with the subgroup.


class Delivery(models.Model):
    """A command of products, for a given network. It's referenced by product
    descriptions and by purchase orders.

    It can be open (regular users are allowed to make and modify purchases),
    closed (only subgroup staff members can modify purchases), or
    delivered (nobody can modify it)."""

    OPEN = 'O'
    CLOSED = 'C'
    DELIVERED = 'D'
    STATE_CHOICES = ((OPEN, "Open"),
                     (CLOSED, "Closed"),
                     (DELIVERED, "Delivered"))
    name = models.CharField(max_length=64)
    network = models.ForeignKey(Network)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=CLOSED)

    def __unicode__(self):
        return "%s/%s" % (self.network.name, self.name)

    def is_open(self):
        return self.state == self.OPEN

    class Meta:
        verbose_name_plural = "Deliveries"


class Product(models.Model):
    """A product is only valid for one delivery. If the same product is valid across
    several deliveries, there are several homonym products in DB, one per delivery,
    so that changes in properties (prices, quotas etc.) don't affect other deliveries.
    """

    name = models.CharField(max_length=64)
    delivery = models.ForeignKey(Delivery)
    price = models.DecimalField(decimal_places=2, max_digits=6)
    quantity_per_package = models.IntegerField(null=True, blank=True)
    unit = models.CharField(max_length=64, null=True, blank=True)
    quantity_limit = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # TODO: if quantity_limit changes, update granted quantities for all affected purchases
        super(Product, self).save(force_insert, force_update, using, update_fields)


class Purchase(models.Model):
    """A purchase is an intent to acquire quantity of a product  a delivery.
    If the product isn't available in unlimited quantity, then the ordered quantity
    might differ from the granted one."""

    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    ordered = models.DecimalField(decimal_places=3, max_digits=6)
    granted = models.DecimalField(decimal_places=3, max_digits=6)

    @property
    def is_satisfied(self):
        return self.granted == self.ordered

    @property
    def price(self):
        return self.granted * self.product.price

    def __unicode__(self, specify_user=True):
        if self.ordered == self.granted:
            fmt = u"%(granted)g %(unit)s %(prod_name)s à %(price).2f€"
        else:
            fmt = u"%(granted)g %(unit)s (au lieu de %(ordered)g) %(prod_name)s à %(price).2f€"
        result = fmt % {
            'granted': self.granted,
            'ordered': self.ordered,
            'unit': plural(self.product.unit, self.granted),
            'prod_name': articulate(self.product.name, self.granted),
            'price': self.granted * self.product.price,
            'user_name': self.user.__unicode__()
        }
        if specify_user:
            result += " pour %s %s" % (self.user.first_name, self.user.last_name)
        return result

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # TODO: if product has limitations, update granted quantities for all affected purchases
        super(Purchase, self).save(force_insert, force_update, using, update_fields)


class Order(object):
    """Sum-up of what a given user has ordered in a given delivery."""

    def __init__(self, user, delivery, purchases=None):
        """Create the order sum-up.
        :param user: who ordered
        :param delivery: when
        :param purchases: if the list of purchases is passed, it isn't extracted from delivery and user.
            Intended for internal use.
        :return: an instance with fields `user`, `delivery`, `price` and `purchases`
        (an iterable of relevant `Purchase` instances)."""

        self.user = user
        self.delivery = delivery
        if purchases:
            self.purchases = purchases
            self.price = None
        else:
            self.purchases = Purchase.objects.filter(product__delivery=delivery, user=user)
            self.price = sum(p.price for p in self.purchases)

    @classmethod
    def by_user_and_product(cls, delivery, users, products=None):
        """Compute a dict of orders, for several users, more efficiently than by performing `len(users)` DB queries.
        Purchases are in a list, sorted according to the list `product` if passed, by product name otherwise.
        If a product hasn't been purchased by a user, `None` is used as a placeholder in the purchases list.

        :param delivery: for which delivery
        :param users: iterable over users
        :param products: ordered list of products; normally, the products available in `delivery`.
        :return: a user -> orders_list_indexed_as_products dictionary for all `users`."""

        class DummyPurchase(object):
            """"Dummy purchase, to be used as a stand-in in purchas tables when a product
            hasn't been purchased by a user."""
            def __init__(self, product, user):
                self.product = product
                self.user = user
                self.price = 0
                self.ordered = 0
                self.granted = 0

            def __nonzero__(self):
                return False

        if not products:
            products = delivery.product_set.order_by('name')
        purchases_by_user = {u: {} for u in users}
        prices = {u: 0 for u in users}
        for pc in Purchase.objects.filter(product__delivery=delivery, user__in=users):
            purchases_by_user[pc.user][pc.product] = pc
            prices[pc.user] += pc.price

        def purchase_line(u):
            return [purchases_by_user[u].get(pd, None) or DummyPurchase(pd, u) for pd in products]

        orders = {u: Order(u, delivery, purchases=purchase_line(u)) for u in users}
        for u in users:
            orders[u].price = prices[u]
        return orders
