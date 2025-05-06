from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from store.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


# ADDING TO THE CART
def add_cart(request, product_id):
    current_user = request.user

    # first get the product using the product_id
    product = Product.objects.get(pk=product_id)

    # if the user is authenticated
    if current_user.is_authenticated:
        # create an empty product variation list
        product_variation = []
        if request.method == "POST":
            # check all the items in the post request to get the variations
            for item in request.POST:
                key = item
                value = request.POST[key]

                # get only the variations from the POST request
                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)

                    product_variation.append(variation)
                except:
                    pass

        # Get the Cart Item for the Cart of the user
        cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()

        # check if the cart item already exists like the one we are trying to add. We have to check the variation as well within this block even if the cart item exists
        if (cart_item_exists):
            cart_item = CartItem.objects.filter(
                product=product, user=current_user)

            # Checking the variations of the product, for this we need:
            # existing variations from database
            # current variations from product_variations above
            # item_id from database

            existing_variation_list = []
            id = []

            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            # check if the currrent variation is in existing variation list
            if product_variation in existing_variation_list:
                # increase the cart quantity of this product
                # we need id of this product with variations first
                index = existing_variation_list.index(product_variation)
                item_id = id[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                # create a new product with current variations
                item = CartItem.objects.create(
                    product=product,
                    user=current_user,
                    quantity=1,
                )

                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        # if there is no cart item like the one we are adding
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()

                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect("cart")

    # if the user is not authenticated
    else:
        # same as above with one key change; instead of user=current_user, we use the cart for non logged in users since they are not the user

        product_variation = []
        if request.method == "POST":

            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)

                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()

        cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()

        if (cart_item_exists):
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            existing_variation_list = []
            id = []

            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1,
                )

                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
        if len(product_variation) > 0:
            cart_item.variations.clear()

            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect("cart")


# REMOVING ONE ITEM FROM THE CART USING MINUS
def remove_cart(request, product_id, cart_item_id):

    # get the product
    product = get_object_or_404(Product, pk=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product,
                user=request.user,
                id=cart_item_id,
            )
        else:
            # get the cart
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # get the cart item using cart item id so that we dont delete other product with diff variations
            cart_item = CartItem.objects.get(
                product=product,
                cart=cart,
                id=cart_item_id
            )

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect("cart")


# REMOVING THE ENTIRE PRODUCT
def remove_cart_item(request, product_id, cart_item_id):

    # get the product
    product = get_object_or_404(Product, pk=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        # get the cart
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # get the cart_item using the cart_item_id so that we don't delete other product with diff variations
        cart_item = CartItem.objects.get(
            product=product,
            cart=cart,
            id=cart_item_id
        )

    cart_item.delete()
    return redirect("cart")


# THE CART
def cart_view(request):
    total = 0
    quantity = 0
    cart_items = []
    tax = 0
    grand_total = 0

    try:

        if request.user.is_authenticated:
            # For logged in users, the cart items are imported when they were not logged in
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            # if the user is not logged in and added cart items, this will display cart items
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (10 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    return render(request, "store/cart.html", {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    })


#CHECKOUT VIEW
@login_required(login_url="login")
def checkout(request):
    total = 0
    tax = 0
    quantity = 0
    cart_items = []
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (10 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    return render(request, "store/checkout.html", {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    })
