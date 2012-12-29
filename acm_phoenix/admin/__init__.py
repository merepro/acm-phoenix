from acm_phoenix import db, admin
from flask.ext.admin import Admin

from acm_phoenix.admin.models import (UserAdmin, ReportAdmin, 
                                      PostAdmin, CategoryAdmin, TagAdmin)

# User Admin Views
admin.add_view(UserAdmin(db.session))
admin.add_view(ReportAdmin(db.session))
admin.add_view(PostAdmin(db.session))
admin.add_view(CategoryAdmin(db.session))
admin.add_view(TagAdmin(db.session))
