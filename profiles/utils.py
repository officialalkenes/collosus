import uuid


def user_directory_path(instance, filename):
    return "user_{0}/{1}".format(instance.user.username, filename)


def try_path(instance, filename):
    return f"user_{instance.user.username}/{filename}"


def get_referral_code():
    code = str(uuid.uuid4()).replace("-", "")[:8]
    return code
