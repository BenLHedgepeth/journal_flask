
import models

def verify_login_credentials(form):
    site_member = models.Writer.get_or_none(
      models.Writer.user_name == form.user_name.data
    )
    if site_member:
      stored_password = site_member.password
      provided_password = form.password.data
      password_accepted = flask_bcrypt.check_password_hash(
        stored_password, provided_password
      )

      if password_accepted:
        return site_member
      elif not password_accepted:
        return None
    return  

