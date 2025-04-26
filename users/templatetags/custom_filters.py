from django import template

register = template.Library()

@register.filter
def format_page_title(value):
    if not value:
        return "Dashboard"
    
    # Special cases for specific pages
    title_map = {
        'ride-list': 'My Rides',
        'vehicle-list': 'My Vehicles',
        'dashboard-home': 'Dashboard',
        'ride-create': 'Offer a Ride',
        'ride-search': 'Find Rides',
        'my-rides': 'My Rides',
        'my-bookings': 'My Bookings',
        'wallet': 'My Wallet',
        'transaction-history': 'Transaction History',
        'profile': 'My Profile',
        'settings': 'Settings'
    }
    
    # Return mapped title if exists
    if value in title_map:
        return title_map[value]
    
    # Otherwise format the string
    return value.replace('-', ' ').replace('_', ' ').title() 