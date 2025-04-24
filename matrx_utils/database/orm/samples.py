from database.orm.supabase.core.fields import (
    CharField,
    IntegerField,
    DateTimeField,
    EmailField,
    JSONField,
)


class User(Model):
    name = CharField(max_length=100, nullable=False)
    age = IntegerField(nullable=True)
    email = EmailField(unique=True)
    created_at = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(auto_now=True)
    preferences = JSONField(default={})


# Assuming we have User and Post models

# Complex query example
active_users_with_recent_posts = (
    User.objects.filter(is_active=True).annotate(post_count=Count("posts")).filter(post_count__gt=0).prefetch_related("posts").order_by("-last_login").limit(10)
)

for user in active_users_with_recent_posts:
    print(f"{user.username} has {user.post_count} posts:")
    for post in user.posts[:5]:  # Only show up to 5 most recent posts
        print(f"- {post.title}")

# Aggregation example
from supabase_orm.query.functions import Avg, Max

average_and_max_age = User.objects.filter(country="US").annotate(avg_age=Avg("age"), max_age=Max("age")).values("avg_age", "max_age").get()

print(f"Average age: {average_and_max_age['avg_age']}")
print(f"Maximum age: {average_and_max_age['max_age']}")


from supabase_orm.operations import create, read, update, delete

# Create
new_user = create.create(User, username="johndoe", email="john@example.com")

# Read
active_users = read.filter(User, is_active=True)
user_count = read.count(User, country="US")

# Update
updated_count = update.update(User, {"is_active": False}, last_login__lt=one_year_ago)
user, created = update.update_or_create(User, {"last_login": now()}, username="johndoe")

# Delete
deleted_count = delete.delete(User, is_active=False, last_login__lt=one_year_ago)
delete.soft_delete(User, id=user_id)

# Bulk operations
new_users = create.bulk_create(
    User,
    [
        {"username": "user1", "email": "user1@example.com"},
        {"username": "user2", "email": "user2@example.com"},
    ],
)

update.bulk_update(User, users_to_update, ["is_active", "last_login"])
