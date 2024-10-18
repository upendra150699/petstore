from django.shortcuts import render,redirect
from petapp.models import Pet, Cart, Profile, Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.messages import success, error, warning
from django.contrib import messages
from django.db.models import Q
import razorpay
from django.core.mail import send_mail
# from petapp import Cart
# Create your views here.\

categories = Pet.objects.values('type').distinct()

def home(request):
    # print('after login in home:',request.user.is_authenticated)
    context={}
    data=Pet.objects.all()
    context['pets']=data
    # catogories = Pet.objects.values('type').distinct()
    # print(catogories)
    context['type']= categories
    return render(request,'index.html', context)

def register(request):
    if request.method=="GET":
        context={}
        context['type']= categories
        return render(request,'register.html', context)
    else:
        context={}
        u=request.POST['username']
        e=request.POST['email']
        p=request.POST['password']
        cp=request.POST['confirmpassword']
        # user=User.objects.get(username=u)
        if u=='' or e=='' or p=='':
            context['error']='Please fill all details'
            return render(request,'register.html',context)
        elif p!=cp:
            context['error']='Password and confirm password must be same'
            return render(request,'register.html',context)
        elif User.objects.filter(username=u).exists():
            context['error']='Username already exist!! Kindly use different Username'
            return render(request,'register.html',context)
        else:        
            user=User.objects.create(username=u,email=e)
            user.set_password(p)  #password encryption
            user.save()
            # context['success']='Registered successfully!! Plaese Login'
            # return render(request,'login.html',context)
            messages.success(request,'Registered successfully!! Plaese Login') 
            return redirect('/userlogin')
        
def userlogin(request): # name can't be login
    if request.method=='GET':
        context={}
        context['type']= categories
        return render(request,'login.html', context)
    else:
        context={}
        # user login code
        u=request.POST['username']
        p=request.POST['password']
        user=authenticate(username=u, password=p)
        if user is None:
            print('wrong credintials')
            context['error']='Kindlay enter correct details to login'
            return render(request,'login.html',context)
        else:
            print('Successfully authentication')
            print(request.user.is_authenticated)
            login(request,user)
            messages.success(request,'Logged in successfully!!')
            return redirect('/')

def userlogout(request):
    logout(request)
    messages.success(request,'Logged out successfully!!')
    return redirect('/')

def contactus(request):
    context={}
    context['type']= categories
    return render(request,'contactus.html', context)

def aboutus(request):
    context={}
    context['type']= categories
    return render(request,'aboutus.html',context)

def petDetails(request,petid):
    data=Pet.objects.get(id=petid)
    context={}
    context['pet']=data
    return render(request,'details.html',context)

def searchByCategory(request, searchBy):
    data = Pet.objects.filter(type = searchBy)
    # select * from pet where type = searchBy
    context={}
    context['pets']=data
    return render(request,'index.html',context)

def searchByRange(request):
    # select * from pet where price >= 15000 and price <= 20000;
    minprice = request.GET['min']
    maxprice = request.GET['max']
    c1 = Q(price__gte = minprice)
    c2 = Q(price__lte = maxprice)
    data = Pet.objects.filter(c1 & c2)
    context={}
    context['pets'] = data
    return render(request,'index.html',context)

def sortPetsByPrice(request,dir):
    # data = Pet.objects.all().order_by('price')
    if dir == 'asc':
        col='price'
    else:
        dir == '-price'
    data = Pet.objects.all().order_by(col)
    context={}
    context['pets']=data
    return render(request,'index.html',context)

def addToCart(request,petid):
    userid = request.user.id
    if userid:
        pet = Pet.objects.get(id=petid)
        cart = Cart.objects.create(petid = pet, uid =request.user)
        cart.save()
        messages.success(request,'Pet added to cart successfully!!') 
        return redirect('/')
    else:
        messages.success(request,'pet add to cart Succefully !!')
        return redirect('/userlogin')
    
def showMyCart(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context={}
    context['cartlist'] = data
    count = len(data)
    total = 0
    for cart in data:
        total += cart.petid.price*cart.quantity
    context['count'] = count
    context['total'] = total
    return render(request,'cart.html',context)

def removeCart(request, cartid):
    cart = Cart.objects.filter(id = cartid)
    cart.delete()
    messages.success(request,'Pet removed from cart Succefully !!')
    return redirect('/mycart')

def updateQuantity(request,cartid,oprn):
    if oprn =='incr':
        cart = Cart.objects.filter(id = cartid)
        qty = cart[0].quantity
        cart.update(quantity = qty+1)
        return redirect('/mycart')
    else:
        cart = Cart.objects.filter(id = cartid)
        qty = cart[0].quantity
        cart.update(quantity = qty-1)
        return redirect('/mycart')

    
def confirmOrder(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    context={}
    context['cartlist'] = data
    count = len(data)
    total = 0
    for cart in data:
        total += cart.petid.price*cart.quantity
    context['count'] = count
    context['total'] = total
    context['profile']=Profile.objects.get(id=userid)
    return render(request,'confirmorder.html',context)
   
def addProfile(request):
    if request.method=="GET":
        return render(request,'profile.html')
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        m = request.POST['mobile']
        a = request.POST['address']

        userid = request.user.id
        user = User.objects.filter(id = userid)
        user.update(first_name=fn, last_name=ln)

        profile = Profile.objects.create(id = user[0], mobile = m, address = a)
        profile.save()
        messages.success(request,'Profile Updated Succefully !!')
        return redirect('/')

def makePayment(request):
    userid = request.user.id
    data = Cart.objects.filter(uid = userid)
    total = 0
    for cart in data:
        total += cart.petid.price*cart.quantity
    client = razorpay.Client(auth=("rzp_test_kkOWC1YlmXWtmN", "s4vYTxPkdK7bz7BDUMnmzPrP"))

    data = { "amount": total*100, "currency": "INR", "receipt": "order_rcptid_11" }
    payment = client.order.create(data=data)
    print(payment)
    context={}
    context['data'] = payment
    return render(request,'pay.html',context)


# def placeOrder(request, ordid):
#     userid = request.user.id
#     # user=User.objects.get(id=userid)
#     cartlist = Cart.objects.filter(uid = userid)
#     for cart in cartlist:
#         # pet = Pet.objects.get(id=cart.petid)
#         order=Order.objects.create(orderid=ordid, userid= cart.uid, petid= cart.petid, quantity = cart.quantity)
#         order.save()
#     cartlist.delete()
#     # sending mail
#     msg="Thank you doe placing the order. Your oder id is: "+ordid
#     send_mail(
#         "Order placed Succefully !!",
#         msg,
#         "sharma.upendra1599@gmail.com",
#         ["request.user.email"],
#         fail_silently=False,
# )
#     messages.success(request,'Order placed Succefully !!')
#     return redirect('/')


def placeOrder(request,ordid):
    '''
    1. userid
    2. cart fetch
    3. insert order details
    4. cart clear
    5. send gmail
    6. home--> 'order placed'
    '''
    userid = request.user.id
    # user = User.objects.get(id = userid)
    cartlist = Cart.objects.filter(uid = userid)
    for cart in cartlist:
        # pet = Pet.objects.get(id = cart.petid)
        order = Order.objects.create(orderid = ordid, userid = cart.uid, petid = cart.petid, quantity = cart.quantity )
        order.save()
    cartlist.delete()
    #sending gmail
    msg = 'Thank you for placing the order. Your order id is:' +ordid
    send_mail(
        "Order Placed successfully",
        msg,
        "sharma.upendra1599@gmail.com",
        [request.user.email],
        fail_silently=False,
    )
    messages.success(request,'Order placed Successfully !!')
    return redirect('/')