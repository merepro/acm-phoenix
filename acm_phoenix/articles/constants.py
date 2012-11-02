"""Constants used in the Article Views and Models"""

DEFAULT = "created"
RECENCY = "created DESC"
TITLE = "title"
CAT_NAME = "articles_category.slug"
TAG_NAME = "tags"
AUTHOR_NAME = "users_user.name"
ORDER = {
    DEFAULT: "Recency",
    RECENCY: "Recency",
    TITLE: "Post Title",
    CAT_NAME: "Category Name",
    TAG_NAME: "Tag Name",
    AUTHOR_NAME: "Author Name"
}
