from asyncio import queues
from csv import QUOTE_NONE
from itertools import product
from multiprocessing import context
from re import template
from turtle import title
from unicodedata import category
from debugpy import connect
from django.shortcuts import redirect, render
from django.views import View
from flask import template_rendered
from .models import Customer,Product,Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from app.models import Product
import pandas as pd
import pickle
import requests
import streamlit as st



class ProductView(View):
    def get(self,request):
        highcalories = Product.objects.filter(category='HC')
        print(highcalories)
        lowcalories = Product.objects.filter(category='LC')
        culturalfoods = Product.objects.filter(category='C')
        return render(request, 'app/home.html', {'highcalories':highcalories,'lowcalories':lowcalories,'culturalfoods':culturalfoods})




class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product = product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html',
        {'product':product, 
        'item_already_in_cart':item_already_in_cart}
        )

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_ammount = 70
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
                totalamount= amount + shipping_ammount
            return render(request, 'app/addtocart.html',{'carts':cart, 'totalamount':totalamount, 'amount':amount})
        else:
            return render(request, 'app/emptycart.html')

@login_required
def plus_cart(request):
        if request.method =='GET':
            prod_id = request.GET['prod_id']
            print(prod_id)
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.quantity+=1
            c.save()
            amount= 0.0
            shipping_amount = 70.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
                

        data = {
                    'quantity': c.quantity,
                    'amount':amount,
                    'totalamount':amount + shipping_amount
                }

        return JsonResponse(data)


@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request,'app/address.html', {'add':add})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':op})




class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',
        {'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congrates!! you have been registered')
            form.save()
        return render(request, 'app/customerregistration.html',
        {'form':form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile has been Added sucessfully')
            return render(request, 'app/profile.html',{'form':form,'active':'btn-primary'})


@login_required
def minus_cart(request):
        if request.method =='GET':
            prod_id = request.GET['prod_id']
            print(prod_id)
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.quantity-=1
            c.save()
            amount= 0.0
            shipping_amount = 70.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
                

        data = {
                'quantity': c.quantity,
                'amount':amount,
                'totalamount':amount + shipping_amount


                }

        return JsonResponse(data)

@login_required
def remove_cart(request):
        if request.method =='GET':
            prod_id = request.GET['prod_id']
            print(prod_id)
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            
            c.delete()
            amount= 0.0
            shipping_amount = 70.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
                

        data = {
                 'quantity': c.quantity,
                 'amount':amount,
                  'totalamount':amount + shipping_amount


                }

        return JsonResponse(data)

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
                for p in cart_product:
                    tempamount = (p.quantity * p.product.selling_price)
                    amount += tempamount
                totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add': add, 'totalamount':totalamount, 'cart_items':cart_items})


def Menu(request):

    highcalories = Product.objects.filter(category='HC')
        
    lowcalories = Product.objects.filter(category='LC')
    return render(request, 'app/Menu.html',{'highcalories':highcalories,'lowcalories':lowcalories})



@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('orders')

def search(request):
    products = ''
    # foodlist = []
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        
      
        if keyword:
            products = Product.objects.filter(
                Q(title__icontains=keyword) )
            # recommendation = recommend(products)
            # #title = products.title
            # food_list = []

            # for i in recommendation:
            #         food = products.objects.get(title=i)
            #         food_list.append(food)          
            # print(i)   
    context = {
       'products': products
              }

    
    return render(request, 'app/search.html', context)



def recommend(request):
    food = pickle.load(open('food.pkl','rb'))
    
    # foods = pd.DataFrame(food)
    # similarity =  pickle.load(open('similarity.pkl','rb'))
   
    
    # food_index = food[food['title'] == foods].index[0]
    # distances = similarity[food_index]
    # # food_list = sorted(list(enumerate(distances)),reverse=True, key=lambda x: x[1])[1:6]
    
    # recommended_foods = []
        
    # for i in food_list:
    #     recommended_foods.append(food_list.iloc[i[0]].title)
    # return recommended_foods

    


    

    params ={ 'allposts': food}
    
    

    return render(request, 'app/recommendation.html', params)



##recommendation here
