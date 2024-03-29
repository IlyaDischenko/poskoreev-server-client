from datetime import datetime, timedelta, timezone

from fastapi import Request, Response, HTTPException

from app.orders.models import Order, OrderLog, CartItem, OrderPayType
from app.restaurants.models import RestaurantPayType, PayType
from app.promocodes.models import PromoCode
from app.users.models import User


async def OrderCheckOrCreate(cookies, user_id, response):
    if '_ri' not in cookies: raise HTTPException(status_code=400, detail={
                'status': 206,
                'message': "Выберете ресторан"
            })
    if '_si' not in cookies: raise HTTPException(status_code=400, detail={
                'status': 204,
                'message': "Выберете улицу"
            })
    _rid = cookies['_ri']
    _sid = cookies['_si']
    rid=int(_rid)
    sid=int(_sid)
    if '_oi' not in cookies:
        order = await Order.create(restaurant_id=rid, address_id=sid, user_id=user_id,
                                   invalid_at=datetime.now(tz=timezone.utc) + timedelta(days=1))
        await OrderLog.create(order_id=order.id)

        response.set_cookie('_oi', value=order.id, httponly=True, secure=True, samesite='none')
        return order
    order = await Order.get_or_none(id=cookies['_oi'], user=user_id)
    if not order:
        order = await Order.create(restaurant_id=rid, address_id=sid, user_id=user_id,
                                   invalid_at=datetime.now(tz=timezone.utc) + timedelta(days=1))
        await OrderLog.create(order_id=order.id)
        response.set_cookie('_oi', order.id, httponly=True, secure=True, samesite='none')
    if order.invalid_at <= datetime.now(tz=timezone.utc):
        log = await OrderLog.get(order_id=order.id)
        log.status = 2
        await log.save()
        order = await Order.create(restaurant_id=rid, address_id=sid, user_id=user_id,
                                   invalid_at=datetime.now(tz=timezone.utc) + timedelta(days=1))
        await OrderLog.create(order_id=order.id)
        response.set_cookie('_oi', order.id, httponly=True, secure=True, samesite='none')
    return order

async def check_all_cookies(cookies):
    if '_oi' not in cookies: raise HTTPException(status_code=400, detail={
        'status': 502,
        'message': "Сначала нужно добавить что-нибудь в корзину"
    })
    if '_ci' not in cookies: raise HTTPException(status_code=400, detail={
        'status': 202,
        'message': "Пожалуйста, выберите город"
    })
    if '_ri' not in cookies: raise HTTPException(status_code=400, detail={
        'status': 206,
        'message': "Пожалуйста, выберите рестр"
    })
    if '_si' not in cookies: raise HTTPException(status_code=400, detail={
        'status': 204,
        'message': "Пожалуйста, выберите улицу"
    })

async def check_order_payment_type(order):
    opt=await OrderPayType.get_or_none(order_id=order.id)
    if not opt: raise HTTPException(status_code=400, detail={
        'status': 503,
        'message': "Выберите способ оплаты"
    })
    rpt= await RestaurantPayType.get_or_none(available=True, id=opt.restaurant_pay_type_id)
    if not rpt: raise HTTPException(status_code=400, detail={
        'status': 208,
        'message': "К сожалению, сейчас мы не принимает оплату вашим способом"
    })
    return rpt.pay_type_id

async def CalculateOrder(order):
    sum = 0
    count = 0
    bonuses = 0
    items = await CartItem.filter(order_id=order.id).prefetch_related('product')
    for item in items:
        count += item.quantity
        sum += item.sum
        bonuses += item.bonuses
    order.products_count = count
    order.added_bonuses = bonuses
    order.sum = int(sum)
    await order.save()
    # return order


async def GetOrderInJSON(order):
    cart_list = []
    items = await CartItem.filter(order_id=order.id).prefetch_related('product', 'menu').order_by('id')
    for item in items:
        cart_list.append({'id': item.menu_id,
                          'title': item.product.title,
                          'img': item.product.img,
                          'quantity': item.quantity,
                          'unit': item.menu.unit,
                          'size': item.menu.size,
                          'sum': item.sum,
                          'bonuses': item.bonuses})
    return {
        'items': cart_list,
        'bonuses': order.added_bonuses,
        'product_count': order.products_count,
        'sum': order.sum,
        'promocode': order.promocode,
        'valid': order.promocode_applied,
        'total_sum': order.sum if not order.total_sum else order.total_sum
    }

async def validate_menu(order):
    listt = []
    items = await CartItem.filter(order_id=order.id).prefetch_related('product', 'menu')
    if not items: raise HTTPException(status_code=400, detail={
                'status': 504,
                'message': "Пустой заказ"
            })
    for item in items:
        if not item.menu.in_stock or not item.menu.visible:
            listt.append({'id': item.menu_id})
            raise HTTPException(status_code=400, detail={
                'status': 402,
                'message': f"these items arent viable: {listt}"
            })
    return

async def AddPromocode(order, input_promocode, user_id):
    short_promocode = input_promocode
    if short_promocode is None or short_promocode == '':
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = None
        order.promocode_linked = False
        await order.save()
        return {
            'promocode': '',
            'applied': False,
            'linked': False,
            'message': '',
        }
    promocode = await PromoCode.get_or_none(short_name=short_promocode, is_active=True)
    if not promocode:
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = None
        order.promocode_linked = False
        await order.save()
        return {
            'promocode': short_promocode,
            'applied': False,
            'linked': False,
            'message': 'Такого промокода не существует',
        }
    # Проверка на привязку промокода юзеру если он не для всех
    if not promocode.for_all:
        user = await User.get(id=user_id).prefetch_related('promocodes')
        user_promocode = await user.promocodes.filter(id=promocode.id)
        if len(user_promocode) == 0:
            order.total_sum = order.sum
            order.promocode_applied = False
            order.promocode = None
            order.promocode_linked = False
            await order.save()
            return {
                'promocode': short_promocode,
                'applied': False,
                'linked': False,
                'message': 'Такого промокода не существует',
            }

    if promocode.count == 0 or promocode.end_day < datetime.now(timezone.utc) or promocode.start_day > datetime.now(timezone.utc):
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = None
        order.promocode_linked = False
        await order.save()
        return {
            'promocode': short_promocode,
            'applied': False,
            'linked': False,
            'message': 'Промокод недействителен',
        }
    if promocode.min_sum > order.sum:
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = short_promocode
        order.promocode_linked = True
        await order.save()
        return {
            'promocode': short_promocode,
            'applied': False,
            'linked': True,
            'message': f'Минимальная сумма заказа для применения промокода {promocode.min_sum}р',
        }

    if promocode.type == 2:
        order.total_sum = round(order.sum * (1 - promocode.effect * 0.01), 0)
        order.promocode_applied = True
        order.promocode_linked = True
        order.promocode = short_promocode
        await order.save()
        return {
            'promocode': short_promocode,
            'applied': True,
            'linked': True,
            'message': 'Промокод применён',
        }
    elif promocode.type == 3:
        order.total_sum = order.sum - promocode.effect
        order.promocode_applied = True
        order.promocode_linked = True
        order.promocode = short_promocode
        await order.save()
        return {
            'promocode': short_promocode,
            'applied': True,
            'linked': True,
            'message': 'Промокод применён',
        }

async def validate_promocode(order, promocode, user_id):
    short_promocode = promocode
    promocode = await PromoCode.get_or_none(short_name=promocode)
    if not promocode:
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = None
        order.promocode_linked = False
        await order.save()
        raise HTTPException(status_code=400, detail={
            'promocode': short_promocode,
            'applied': False,
            'linked': False,
            'status': 301,
            'message': 'Такого промокода не существует',
        })
    # Проверка на привязку промокода юзеру если он не для всех
    if not promocode.for_all:
        user = await User.get(id=user_id).prefetch_related('promocodes')
        user_promocode = await user.promocodes.filter(id=promocode.id)
        if len(user_promocode) == 0:
            order.total_sum = order.sum
            order.promocode_applied = False
            order.promocode = None
            order.promocode_linked = False
            await order.save()
            raise HTTPException(status_code=400, detail= {
                'promocode': short_promocode,
                'applied': False,
                'linked': False,
                'status': 302,
                'message': 'Такого промокода не существует',
            })

    if promocode.count==0 or promocode.end_day < datetime.now(timezone.utc) or promocode.start_day > datetime.now(timezone.utc):
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = None
        order.promocode_linked = False
        await order.save()
        raise HTTPException(status_code=400, detail= {
            'promocode': short_promocode,
            'applied': False,
            'linked': False,
            'status': 303,
            'message': 'Промокод недействителен',
        })
    if promocode.min_sum > order.sum:
        order.total_sum = order.sum
        order.promocode_applied = False
        order.promocode = short_promocode
        order.promocode_linked = True
        await order.save()
        raise HTTPException(status_code=400, detail= {
            'promocode': short_promocode,
            'applied': False,
            'linked': True,
            'status': 304,
            'message': f'Минимальная сумма заказа для применения промокода {promocode.min_sum}р',
        })

    if promocode.type == 2:
        order.total_sum = round(order.sum * (1 - promocode.effect * 0.01), 2)
        order.promocode_applied = True
        order.promocode_linked = True
        order.promocode = short_promocode
        await order.save()
        return
    elif promocode.type == 3:
        order.total_sum = order.sum - promocode.effect
        order.promocode_applied = True
        order.promocode_linked = True
        order.promocode = short_promocode
        await order.save()
        return
