from datetime import timezone
import random
from urllib import request
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import FarmerDetailsForm,FarmerDetails,RambutanPostForm,RegisterUserForm, WishlistForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  BillingDetail, Cart, CustomerDetails, FarmerDetails, Order, OrderItem, OrderNotification, RambutanPost,Registeruser, Wishlist
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.hashers import make_password
from .forms import RegisterUserForm
from .forms import FarmerDetailsForm, TreeVarietyForm, RambutanPostForm
from django.contrib import messages
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_control



def index(request):
    if request.method =='POST':
        pass
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

otp_storage = {}

def send_otp_email(user_email):
    otp = random.randint(1000, 9999) 
    otp_storage[user_email] = otp 

    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Please use this to verify your email.'
    from_email = 'rambutanwarehouse@gmail.com' 
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

def enter_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Registeruser.objects.filter(username=email).exists():
            messages.info(request, "Email is already registered. Please log in.")
            return redirect('login')

        send_otp_email(email)

        request.session['user_email'] = email

        return redirect('verify_otp')

    return render(request, 'enter_email.html')

def verify_otp(request):
    email = request.session.get('user_email') 

    if not email:
        # messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        if otp_storage.get(email) and otp_storage[email] == int(otp_input):
          
            del otp_storage[email]
            request.session['verified_email'] = email

            return redirect('register')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')
'''
def register(request):
    email = request.session.get('verified_email') 

    if not email:
        messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            if email != form.cleaned_data['username']:
                messages.error(request, "Please register with the email you verified.")
                return redirect('register')

            user = form.save(commit=False)
            user.username = email 
            user.is_active = True 
            user.save()

            del request.session['verified_email']

            subject = "Welcome to Our Website"
            message = f"Dear {user.username},\n\nThank you for registering at our website."
            recipient_list = [user.username] 
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, recipient_list)

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterUserForm(initial={'username': email})  

    return render(request, 'register.html', {'form': form})'''
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import login

def register(request):
    # Retrieve email from session (for normal email registration flow)
    email = request.session.get('verified_email') 

    # Check if user is signing in with Google
    if request.user.is_authenticated and request.user.email:
        email = request.user.email  # Use the email provided by Google
        if email:
            request.session['verified_email'] = email  # Store in session for further validation

    # If there's no verified email (either from session or Google), redirect to email entry page
    if not email:
        messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    # If this is a POST request (form submission)
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            if email != form.cleaned_data['username']:
                messages.error(request, "Please register with the email you verified.")
                return redirect('register')

            user = form.save(commit=False)
            user.username = email 
            user.is_active = True  # Automatically activate the user
            user.save()

            # Clear the verified email from the session
            del request.session['verified_email']

            # Send welcome email
            subject = "Welcome to Our Website"
            message = f"Dear {user.username},\n\nThank you for registering at our website."
            recipient_list = [user.username] 
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, recipient_list)

            # Log the user in automatically if Google sign-in
            if request.user.is_authenticated:
                login(request, user)

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        
        # Pre-fill the username field with the verified email
        form = RegisterUserForm(initial={'username': email})

    return render(request, 'register.html', {'form': form})

'''
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        print(username,password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
          
            login(request, user)

            request.session['user_id'] = user.id
            request.session['name'] = user.username
            request.session['role'] = user.role
            if user.is_superuser:  # or user.role == 'admin' if you're using a custom role system
                return redirect('/admin') 
            elif user.role == 'farmer':
                return redirect('farmer_dashboard')
            elif user.role == 'customer':
                return redirect('customer_dashboard')
            else:
                return render(request, 'login.html', {'error': 'Invalid user role'})
        else:
            messages.error(request,message="Invalid Credentials")
    return render(request, 'login.html')
'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        print(username, password)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        print(user)
        
        if user is not None:
            # Log the user in
            login(request, user)
            
            # Set session variables
            request.session['user_id'] = user.id
            request.session['name'] = user.username
            request.session['role'] = user.role
            
            # Check for superuser and redirect to admin dashboard
            if user.is_superuser:  # or user.role == 'admin' if you have custom roles
                return redirect('admin_dashboard')  # Change to the name of your custom admin dashboard URL
            elif user.role == 'farmer':
                return redirect('farmer_dashboard')  # Redirect to farmer dashboard
            elif user.role == 'customer':
                return redirect('customer_dashboard')  # Redirect to customer dashboard
            else:
                # Handle invalid roles (if any)
                return render(request, 'login.html', {'error': 'Invalid user role'})
        else:
            # Handle invalid credentials
            messages.error(request, message="Invalid Credentials")
    
    # Render the login page if GET request
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_dashboard(request):
    try:
        user = Registeruser.objects.get(username=request.user.username,role='farmer')
    except Registeruser.DoesNotExist:
        return render(request, '404.html')  
    return render(request, 'farmer_dashboard.html', {'farmer': user})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_details(request):
    try:
        farmer_details = FarmerDetails.objects.get(user=request.user)
    except FarmerDetails.DoesNotExist:
        farmer_details = None

    if request.method == 'POST':
        address = request.POST.get('address')
        mobile_number = request.POST.get('mobile_number')
        aadhar_number = request.POST.get('aadhar_number')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        bank_name = request.POST.get('bank_name')
        location = request.POST.get('location')
        
        if farmer_details:
            farmer_details.address = address
            farmer_details.mobile_number = mobile_number
            farmer_details.aadhar_number = aadhar_number
            farmer_details.account_number = account_number
            farmer_details.ifsc_code = ifsc_code
            farmer_details.bank_name = bank_name
            farmer_details.location = location
        
            farmer_details.save()
        else:
            farmer_details = FarmerDetails.objects.create(
                user=request.user,
                address=address,
                mobile_number=mobile_number,
                aadhar_number=aadhar_number,
                account_number=account_number,
                ifsc_code=ifsc_code,
                bank_name=bank_name,
                location=location,
               
            )

        return redirect('farmer_dashboard')
    return render(request, 'farmer_details.html', {
        'farmer_details': farmer_details
    })


PRODUCT_CHOICES = [
    ('Muar Gading', 'Muar Gading'),
    ('Caesar', 'Caesar'),
    ('Hg Deli Baling', 'Hg Deli Baling'),
    ('Jarum Emas', 'Jarum Emas'),
    ('E35', 'E35'),
    ('Binjai', 'Binjai'),
    ('Malwana', 'Malwana'),
    ('School Boy', 'School Boy'),
    ('Maharlika', 'Maharlika'),
    ('Rongrien', 'Rongrien'),
    ('Rambutan N18', 'Rambutan N18'),
    ('other', 'Other'),
]
CATEGORY_CHOICES = [
        ('fresh_fruit', 'Fresh Fruit'),
        ('juice', 'Juice'),
        ('pickle', 'Pickle'),
        ('wine', 'Wine'),
        
    ]

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def post_rambutan(request):
    if request.method == "POST":
        product = request.POST.get('product')
        category = request.POST.get('category') 
        quantity_type = request.POST.get('quantity_type')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        description = request.POST.get('description')
        other_product_name = request.POST.get('other_product') if product == 'other' else None
        image = request.FILES.get('image')

        # Retrieve farmer; if not found, redirect to complete profile
        try:
            farmer = FarmerDetails.objects.get(user=request.user)
        except FarmerDetails.DoesNotExist:
           # messages.error(request, _("Please complete your profile before posting."))
            return redirect(reverse('complete_profile'))  # Redirect to profile completion page

        # Ensure 'Other' has a name
        if product == 'other' and not other_product_name:
           # messages.error(request, _("Please enter a product name for 'Other' selection."))
            return redirect(reverse('post_rambutan'))

        # Save the rambutan post
        rambutan_post = RambutanPost(
            farmer=farmer,
            product=other_product_name if product == 'other' else product,
            category=category,
            quantity_type=quantity_type,
            quantity=quantity,
            quantity_left=quantity,
            price=price,
            description=description,
            image=image
        )
        rambutan_post.save()

       # messages.success(request, _("Your rambutan post has been created successfully!"))
        return HttpResponseRedirect(reverse('view_posts'))

    context = {'PRODUCT_CHOICES': PRODUCT_CHOICES}
    return render(request, 'post_rambutan.html', context)

def create_tree_variety(request):
    if request.method == 'POST':
        form = TreeVarietyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('sucess')
        else:
            messages.error(request,message=form.errors)    
    else:
        form = TreeVarietyForm()
    return render(request, 'forms.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_posts(request):
    user = request.user

    try:
        farmer_details = user.farmerdetails

        available_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=True)
        out_of_stock_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=False, quantity_left=0)
        unavailable_posts = RambutanPost.objects.filter(farmer=farmer_details, is_available=False).exclude(quantity_left=0)

    except FarmerDetails.DoesNotExist:
        return redirect('farmer_details')

    context = {
        'available_posts': available_posts,
        'out_of_stock_posts': out_of_stock_posts,
        'unavailable_posts': unavailable_posts,
        'user': user,
    }

    return render(request, 'view_posts.html', context)
'''
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_post(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    farmer_details = get_object_or_404(FarmerDetails, user=request.user) 

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.farmer = farmer_details

            updated_post.quantity_left = updated_post.quantity

            updated_post.is_available = True
            updated_post.save()

            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})

    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})
'''
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import RambutanPost, FarmerDetails
from .forms import RambutanPostForm

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_post(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    farmer_details = get_object_or_404(FarmerDetails, user=request.user)

    if request.method == 'POST':
        form = RambutanPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.farmer = farmer_details

            # Set quantity_left to quantity value
            updated_post.quantity_left = updated_post.quantity

            # Handle "other" product option if selected
            if form.cleaned_data.get('product') == 'other':
                updated_post.product = request.POST.get('other_product')
            else:
                updated_post.product = form.cleaned_data.get('product')

            # Ensure that category is set to avoid IntegrityError
            updated_post.category = form.cleaned_data.get('category')
            updated_post.is_available = True
            updated_post.save()
            return redirect('view_posts')
        else:
            return render(request, 'update_post.html', {'form': form, 'post': post})
    else:
        form = RambutanPostForm(instance=post)
        return render(request, 'update_post.html', {'form': form, 'post': post})

def update_quantity(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity_left')

        if new_quantity is not None:
            try:
                new_quantity = int(new_quantity)
                post.quantity_left = new_quantity
                post.quantity=new_quantity

                if new_quantity > 0:
                    post.is_available = True
                    #messages.success(request, 'Post is now available.')
                else:
                    post.is_available = False
                   # messages.info(request, 'Post is out of stock.')

                post.save()
                return redirect('view_posts')

            except ValueError:
                messages.error(request, 'Please enter a valid number for quantity.')
        else:
            messages.error(request, 'Quantity cannot be empty.')

    return render(request, 'update_quantity.html', {'post': post})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_post_confirmation(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    in_cart = Cart.objects.filter(rambutan_post=post).exists()
    in_wishlist = Wishlist.objects.filter(rambutan_post=post).exists()
    in_order = OrderItem.objects.filter(rambutan_post=post).exists()

    if request.method == 'POST':
        if in_order:
            return redirect('view_posts')

        if in_cart or in_wishlist:
            post.is_available = False 
            post.save()
        else:
            post.delete() 
        
        return redirect('view_posts')

    return render(request, 'delete_post_confirmation.html', {
        'post': post,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'in_order': in_order,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_post(request, id):
    return redirect('delete_post_confirmation', id=id)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmer_orders(request):
    farmer_details = get_object_or_404(FarmerDetails, user=request.user)
    
    farmer_posts = RambutanPost.objects.filter(farmer=farmer_details)
    
    order_items = OrderItem.objects.filter(rambutan_post__in=farmer_posts).select_related('order', 'rambutan_post')

    orders_by_number = {}
    for item in order_items:
        order_number = item.order.order_number  
        if order_number not in orders_by_number:
            orders_by_number[order_number] = []
        orders_by_number[order_number].append(item)

    context = {
        'orders_by_number': orders_by_number,
    }

    return render(request, 'order_farmer.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html', {'cart': cart})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request):
    return render(request, 'edit_profile.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_single(request):
    return render(request, 'product-single.html')


@login_required
def blog(request):
    return render(request, 'blog.html')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile_view(request):
   
    return render(request, 'customer_profile.html')
'''    
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def products_browse(request):
    products = RambutanPost.objects.all().values('id', 'product', 'category', 'image', 'price', 'created_at', 'description', 'is_available', 'quantity_left','farmer','quantity_type')
    
    cart_items = Cart.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)

    for product in products:
        if product['quantity_left'] <= 0:
            product['status_message'] = 'Out of Stock'
        elif not product['is_available']:
            product['status_message'] = 'Unavailable'

    context = {
        'products': products,
    }
    return render(request, 'shop.html', context)
'''
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def products_browse(request):
    category_filter = request.GET.get('category', '')  # Get the selected category from the URL parameters

    # Filter products by category if a category filter is applied
    products_query = RambutanPost.objects.all()
    if category_filter:
        products_query = products_query.filter(category=category_filter)

    products = products_query.values(
        'id', 'product', 'category', 'image', 'price', 'created_at', 'description',
        'is_available', 'quantity_left', 'farmer','quantity_type'
    )

    # Handle cart and wishlist items
    cart_items = Cart.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)
    wishlist_items = Wishlist.objects.filter(user=request.user).values_list('rambutan_post_id', flat=True)

    # Add status messages
    for product in products:
        if product['quantity_left'] <= 0:
            product['status_message'] = 'Out of Stock'
        elif not product['is_available']:
            product['status_message'] = 'Unavailable'

    context = {
        'products': products,
        'category_filter': category_filter  # Pass the selected category to the template
    }
    return render(request, 'shop.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def wishlist(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('rambutan_post')

    wishlists = RambutanPost.objects.filter(id__in=[item.rambutan_post_id for item in wishlist_items])

    return render(request, 'wishlist.html', {'wishlist_items': wishlists})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        rambutan_post=post
    )

    if not post.is_available and created:
        messages.warning(request, f"{post.name} is currently unavailable, but it has been added to your wishlist.")

    return redirect('wishlist')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def remove_from_wishlist(request, id):
    post = get_object_or_404(RambutanPost, id=id)
    wishlist_item = Wishlist.objects.filter(user=request.user, rambutan_post=post).first()

    if wishlist_item:
        wishlist_item.delete()

    return redirect('wishlist')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request, rambutan_post_id):
    rambutan_post = get_object_or_404(RambutanPost, id=rambutan_post_id)

    if not rambutan_post.is_available:
        messages.warning(request, f"{rambutan_post.name} is currently unavailable. You can keep it in your cart but cannot purchase it.")
    else:
        cart_item, created = Cart.objects.get_or_create(
            user=request.user, 
            rambutan_post=rambutan_post,
            defaults={'price': rambutan_post.price} 
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
    
    return redirect('cart')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.price * item.quantity
    total_price = sum(item.total_price for item in cart_items) 
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    
    return render(request, 'cart.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    
    return redirect('cart') 


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_cart_item_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))
        
        rambutan_post = get_object_or_404(RambutanPost, id=cart_item.rambutan_post_id)

        if new_quantity <= rambutan_post.quantity_left:
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
        else:
            messages.error(request, f"Cannot add more than available quantity. Available: {rambutan_post.quantity_left}.")
            return redirect('cart')

    return redirect('cart')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def billing_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
        rambutan_post = cart_item.rambutan_post
        
        if cart_item.quantity > rambutan_post.quantity_left:
            messages.error(request, f"Sorry, the quantity of '{rambutan_post.name}' in your cart exceeds the available stock.")
            return redirect('cart') 
    billing_details = BillingDetail.objects.filter(user=request.user).last()

    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        country = request.POST.get('country')
        street_address = request.POST.get('street-address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        if not all([first_name, last_name, country, street_address, city, postcode, phone, email]):
            messages.error(request, "All fields are required. Please fill in all details.")
            return redirect('place_order')

        if billing_details:
            billing_details.first_name = first_name
            billing_details.last_name = last_name
            billing_details.country = country
            billing_details.street_address = street_address
            billing_details.city = city
            billing_details.postcode = postcode
            billing_details.phone = phone
            billing_details.email = email
            billing_details.save()
        else:
            BillingDetail.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                country=country,
                street_address=street_address,
                city=city,
                postcode=postcode,
                phone=phone,
                email=email
            )

        return redirect('place_order')

    return render(request, 'checkout.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_billing_details(request, pk):
    billing_details = get_object_or_404(BillingDetail, pk=pk)

    if request.method == 'POST':
        billing_details.first_name = request.POST.get('first-name')
        billing_details.last_name = request.POST.get('last-name')
        billing_details.country = request.POST.get('country')
        billing_details.street_address = request.POST.get('street-address')
        billing_details.city = request.POST.get('city')
        billing_details.postcode = request.POST.get('postcode')
        billing_details.phone = request.POST.get('phone')
        billing_details.email = request.POST.get('email')

        try:
            billing_details.full_clean()
            billing_details.save()  
            messages.success(request, 'Billing details updated successfully.')
            return redirect('place_order') 
        except ValidationError as e:
            messages.error(request, f'Error updating billing details: {e}')

    return render(request, 'update_billing_details.html', {'billing_details': billing_details})
'''
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def place_order(request):
    billing_details = BillingDetail.objects.filter(user=request.user).last()

    if not billing_details:
        return redirect('billing_view')

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    unavailable_items = cart_items.filter(rambutan_post__is_available=False)
    if unavailable_items.exists():
        return redirect('cart')

    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 0
    platform_fee = 0
    # discount = 100
    total = subtotal + delivery_fee + platform_fee

    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        order = Order.objects.create(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        for item in cart_items:
            rambutan_post = item.rambutan_post
            ordered_quantity = item.quantity

            if rambutan_post.quantity_left < ordered_quantity:
                return redirect('cart')

            rambutan_post.quantity_left -= ordered_quantity
            if rambutan_post.quantity_left <= 0:
                rambutan_post.is_available = False
            rambutan_post.save()

            OrderItem.objects.create(
                order=order,
                rambutan_post=rambutan_post,
                quantity=ordered_quantity,
                price=item.price
            )

            farmer_details = rambutan_post.farmer  
            register_user = farmer_details.user  

            OrderNotification.objects.create(
                farmer=register_user,  
                order_number=order.order_number,
                item_name=rambutan_post.product,
                quantity=ordered_quantity,
                price=item.price
            )

        cart_items.delete()

        subject = 'Order Confirmation - Order #{}'.format(order.order_number)
        message = (
            f'Thank you for your order!\n\n'
            f'Order Number: {order.order_number}\n'
            f'Total Amount: ₹{total}\n'
            f'Payment Method: {payment_method}\n\n'
            f'We will notify you once your items are ready for shipping.'
        )
        recipient_list = [request.user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'place_order.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee' : platform_fee,
        # 'discount': discount,
        'total': total,
    })
'''
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .models import BillingDetail, Cart, Order, OrderItem, OrderNotification
import razorpay

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def place_order(request):
    billing_details = BillingDetail.objects.filter(user=request.user).last()

    if not billing_details:
        return redirect('billing_view')

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')

    unavailable_items = cart_items.filter(rambutan_post__is_available=False)
    if unavailable_items.exists():
        return redirect('cart')

    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 0
    platform_fee = 0
    total = subtotal + delivery_fee + platform_fee
    print(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY)
    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')

        # Create order object but do not save it yet
        order = Order(
            billing_detail=billing_details,
            user=request.user,
            total_amount=total,
            payment_method=payment_method
        )

        if payment_method == 'Razorpay':
            print(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total * 100),  # amount in paisa
                'currency': 'INR',
                'payment_capture': '1'
            })

            # Save Razorpay order ID in the order model
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            # Redirect to Razorpay payment page
            #return redirect('razorpay_payment_view', order_id=order.id)
            return redirect('razorpay_payment_view', order_number=order.order_number)

        # For other payment methods (e.g., COD)
        order.save()

        for item in cart_items:
            rambutan_post = item.rambutan_post
            ordered_quantity = item.quantity

            if rambutan_post.quantity_left < ordered_quantity:
                return redirect('cart')

            rambutan_post.quantity_left -= ordered_quantity
            if rambutan_post.quantity_left <= 0:
                rambutan_post.is_available = False
            rambutan_post.save()

            OrderItem.objects.create(
                order=order,
                rambutan_post=rambutan_post,
                quantity=ordered_quantity,
                price=item.price
            )

            # Create order notification for the farmer
            farmer_details = rambutan_post.farmer
            register_user = farmer_details.user
            OrderNotification.objects.create(
                farmer=register_user,
                order_number=order.order_number,
                item_name=rambutan_post.product,
                quantity=ordered_quantity,
                price=item.price
            )

        # Clear the cart
        cart_items.delete()

        # Send order confirmation email
        subject = f'Order Confirmation - Order #{order.order_number}'
        message = (
            f'Thank you for your order!\n\n'
            f'Order Number: {order.order_number}\n'
            f'Total Amount: ₹{total}\n'
            f'Payment Method: {payment_method}\n\n'
            f'We will notify you once your items are ready for shipping.'
        )
        recipient_list = [request.user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

        # Redirect to order details
        return redirect('order_detail', order_number=order.order_number)

    return render(request, 'place_order.html', {
        'billing_details': billing_details,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee': platform_fee,
        'total': total,
    })

# views.py
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

def razorpay_payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

    # Payment amount in paise (multiply by 100)
    amount = int(order.total_amount * 100)

    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Store the Razorpay order ID in our order object and save
    order.razorpay_order_id = razorpay_order['id']
    order.save()

    # Pass order data to the template
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
    }

    return render(request, 'razorpay_payment.html', context)
@csrf_exempt
def razorpay_payment_complete(request):
    if request.method == "POST":
        data = request.POST
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
            params_dict = {
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            }

            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Retrieve the order and update payment details
            order = Order.objects.get(razorpay_order_id=data['razorpay_order_id'])
            order.razorpay_payment_id = data['razorpay_payment_id']
            order.razorpay_signature = data['razorpay_signature']
            order.payment_status = 'Completed'
            order.save()

            return redirect('order_detail', order_number=order.order_number)

        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Signature verification failed.")
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order does not exist.")

    return HttpResponseBadRequest("Invalid request.")

from datetime import timedelta
from django.utils import timezone

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        billing_details = order.billing_detail
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 0
        platform_fee = 0
        total = subtotal + delivery_fee + platform_fee
        
       
    except Order.DoesNotExist:
        return redirect('order')

    return render(request, 'order.html', {
        'order': order,
        'order_items': order_items,
        'billing_details': billing_details,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'platform_fee': platform_fee,
        'total': total,
        
    })

'''
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'order_history.html', {
        'orders': orders
    })
'''
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from datetime import timedelta
from .models import Order, OrderItem

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    order_details = []

    for order in orders:
        tracking_stages = ["ordered", "packed", "shipped", "out_for_delivery", "delivered"]
        
        # Set the order status based on the time elapsed since creation
        current_time = timezone.now()
        elapsed_time = current_time - order.created_at

        # Create a dictionary to track the status of each stage
        stage_status = {
            'ordered': 'inactive',
            'packed': 'inactive',
            'shipped': 'inactive',
            'out_for_delivery': 'inactive',
            'delivered': 'inactive'
        }

        # Update the stage_status based on elapsed time
        if elapsed_time < timedelta(days=1):
            stage_status['ordered'] = 'active'
        elif elapsed_time < timedelta(days=2):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
        elif elapsed_time < timedelta(days=4):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
            stage_status['shipped'] = 'active'
        elif elapsed_time < timedelta(days=5):
            stage_status['ordered'] = 'active'
            stage_status['packed'] = 'active'
            stage_status['shipped'] = 'active'
            stage_status['out_for_delivery'] = 'active'
        else:
            for stage in stage_status:
                stage_status[stage] = 'active'

        # Calculate order totals
        order_items = OrderItem.objects.filter(order=order)
        subtotal = sum(item.price * item.quantity for item in order_items)
        delivery_fee = 0  # Set your delivery fee logic here
        platform_fee = 0  # Set your platform fee logic here
        total = subtotal + delivery_fee + platform_fee

        # Check if the order can be deleted
        delete_allowed = order.created_at >= timezone.now() - timedelta(hours=48)

        # Append the order details to the list
        order_details.append({
            'order': order,
            'order_items': order_items,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'platform_fee': platform_fee,
            'total': total,
            'delete_allowed': delete_allowed,
            'stage_status': stage_status,
        })

    return render(request, 'order_history.html', {
        'order_details': order_details,
    })
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Order, OrderItem
from datetime import timedelta

@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Check if the order is eligible for cancellation (created within the last 48 hours)
    if order.created_at >= timezone.now() - timedelta(hours=48):
        # Refill quantity in RambutanPost for each item in the order
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            rambutan_post = item.rambutan_post
            rambutan_post.quantity += item.quantity
            rambutan_post.save()

        # Delete the order without updating its status
        order.delete()

    # Redirect back to the order history page after cancellation
    return redirect('order_history')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_notifications(request):
    notifications = OrderNotification.objects.all().order_by('-created_at')  # Fetching all notifications
    return render(request, 'order_notifications.html', {'notifications': notifications})


from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class CustomPasswordResetView(PasswordResetView):
    template_name = 'custom_password_reset.html'  # Your custom template
    email_template_name = 'custom_password_reset_email.html'  # Your custom email template
    subject_template_name = 'custom_password_reset_subject.txt'  # Your custom subject template
    success_url = reverse_lazy('password_reset_done')  # Redirect URL after success

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'custom_password_reset_confirm.html'  # Your custom template
    success_url = reverse_lazy('password_reset_complete')  # Redirect URL after password reset
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from warehouse.models import FarmerDetails, RambutanPost, Order

# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

# View for the Admin Dashboard
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Fetch data for the dashboard
    total_farmers = FarmerDetails.objects.count()
    total_rambutan_posts = RambutanPost.objects.count()
    total_orders = Order.objects.filter().count()

    # Fetch recent rambutan posts (limit to 5 posts for the dashboard)
    recent_rambutan_posts = RambutanPost.objects.select_related('farmer').order_by('created_at')[:5]

    context = {
        'total_farmers': total_farmers,
        'total_rambutan_posts': total_rambutan_posts,
        'total_orders': total_orders,
        'recent_rambutan_posts': recent_rambutan_posts,
    }

    return render(request, 'admin_dashboard.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from .models import FarmerDetails
from .forms import FarmerDetailsForm  # Import the form
from django.db.models import Q

# View for managing farmers
def manage_farmers(request):
    # Get the search query from the request (if any)
    query = request.GET.get('search', '')

    if query:
        # Filter farmers by name or location based on the search input
        farmers = FarmerDetails.objects.filter(
            Q(user__name__icontains=query) | Q(location__icontains=query)
        )
    else:
        # If no search query, show all farmers
        farmers = FarmerDetails.objects.all()

    # Pass the farmers list to the template
    context = {
        'farmers': farmers
    }

    return render(request, 'manage_farmers.html', context)

# View for editing farmer details
def edit_farmer(request, farmer_id):
    # Fetch the specific farmer based on the provided farmer_id
    farmer = get_object_or_404(FarmerDetails, id=farmer_id)

    if request.method == 'POST':
        # Process the form submission here
        form = FarmerDetailsForm(request.POST, instance=farmer)
        if form.is_valid():
            form.save()
            return redirect('manage_farmers')
    else:
        # Display the form prefilled with the farmer's current details
        form = FarmerDetailsForm(instance=farmer)

    return render(request, 'edit_farmer.html', {'form': form, 'farmer': farmer})

# View for deleting a farmer
def delete_farmer(request, farmer_id):
    # Fetch the farmer and delete them
    farmer = get_object_or_404(FarmerDetails, id=farmer_id)
    farmer.delete()
    return redirect('manage_farmers')  # Redirect back to the manage farmers page after deletion

from django.shortcuts import render, get_object_or_404, redirect
from .models import RambutanPost  # Make sure to import your RambutanPost model
from django.db.models import Q
from .forms import RambutanPostForm  # Import your form for RambutanPost

# View for managing rambutan posts
def manage_rambutan_posts(request):
    # Get the search query from the request (if any)
    query = request.GET.get('search', '')

    if query:
        # Filter rambutan posts by farmer name or variety based on the search input
        rambutan_posts = RambutanPost.objects.filter(
            Q(farmer__user__name__icontains=query) | Q(tree_variety__name__icontains=query)
        )
    else:
        # If no search query, show all rambutan posts
        rambutan_posts = RambutanPost.objects.all()

    # Pass the rambutan posts list to the template
    context = {
        'rambutan_posts': rambutan_posts
    }

    return render(request, 'manage_rambutan_posts.html', context)

# View for editing rambutan post details
def edit_rambutan_post(request, post_id):
    # Fetch the specific post based on the provided post_id
    post = get_object_or_404(RambutanPost, id=post_id)

    if request.method == 'POST':
        # Process the form submission here
        form = RambutanPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('manage_rambutan_posts')  # Redirect to manage page after saving
    else:
        # Display the form prefilled with the post's current details
        form = RambutanPostForm(instance=post)

    return render(request, 'edit_rambutan_post.html', {'form': form})

# View for deleting a rambutan post
def delete_rambutan_post(request, post_id):
    # Fetch the post and delete it
    post = get_object_or_404(RambutanPost, id=post_id)
    post.delete()
    return redirect('manage_rambutan_posts')  # Redirect back to the manage posts page after deletion

from django.shortcuts import render, get_object_or_404, redirect
from .models import Order

# View for displaying all orders
def view_orders(request):
    query = request.GET.get('search', '')
    if query:
        orders = Order.objects.filter(
            Q(order_number__icontains=query) | Q(customer__name__icontains=query)
        )
    else:
        orders = Order.objects.all()

    return render(request, 'view_orders.html', {'orders': orders})

# View for displaying the order details
def view_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'view_order_detail.html', {'order': order})

# View for deleting an order
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('view_orders')

@login_required
def edit_farmer_profile(request):
    # Fetch the current user's `Registeruser` and `FarmerDetails` instances
    user_instance = get_object_or_404(Registeruser, username=request.user.username)
    farmer_details_instance = get_object_or_404(FarmerDetails, user=user_instance)
    
    if request.method == 'POST':
        # If the form is submitted, get the POST data
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        place = request.POST.get('place')
        mobile_number = request.POST.get('mobile_number')
        location = request.POST.get('location')
        aadhar_number = request.POST.get('aadhar_number')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        
        # Update Registeruser instance
        user_instance.name = name
        user_instance.contact = contact
        user_instance.address = address
        user_instance.place = place
        user_instance.save()
        # Update FarmerDetails instance
        farmer_details_instance.mobile_number = mobile_number
        farmer_details_instance.location = location
        farmer_details_instance.aadhar_number = aadhar_number
        farmer_details_instance.bank_name = bank_name
        farmer_details_instance.account_number = account_number
        farmer_details_instance.ifsc_code = ifsc_code
        farmer_details_instance.save()
        # Display success message and redirect
        #messages.success(request, 'Profile updated successfully!')
        return redirect(reverse('farmer_dashboard'))
    
    return render(request, 'edit_farmer_profile.html', {
        'user_instance': user_instance,
        'farmer_details_instance': farmer_details_instance
    })
# views.py
@login_required
def edit_customer_profile(request):
    user = get_object_or_404(Registeruser, username=request.user.username)  # Get the logged-in user's details
    if request.method == 'POST':
        # Update user information
        user.name = request.POST.get('name')
        user.address = request.POST.get('address')
        user.contact = request.POST.get('contact')
        user.place = request.POST.get('place')
        user.save()  # Save the updated details
        #messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile_view')  # Redirect to profile view after saving
    return render(request, 'edit_customer_profile.html', {'user': user})  # Pass user to the template
