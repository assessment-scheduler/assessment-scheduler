from .staff import staff_views
from .index import index_views
from .auth import auth_views
from .admin import admin_views
# from .course import course_views

views = [staff_views, 
               index_views,
               auth_views,
               admin_views,
            # course_views,
         ]
