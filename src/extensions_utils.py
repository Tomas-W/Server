css_bundle = [
        {
            "name": "auth_css",
            "files": [
                "css/settings.css",
                "css/forms_style.css",
                "css/auth/auth_base.css",
                "css/auth/auth.css",
            ],
            "filters": "rcssmin",
            "output": "dist/auth_css.min.css"
        },
        {
            "name": "base_css",
            "files": [
                "css/settings.css",
                "css/forms_style.css",
                "css/base.css",
            ],
            "filters": "rcssmin",
            "output": "dist/base_css.min.css"
        },
        {
            "name": "admin_css",
            "files": [
                "css/admin/admin_base.css"
            ],
            "filters": "rcssmin",
            "output": "dist/admin_css.min.css"
        },
        {
            "name": "all_news_css",
            "files": [
                "css/news/news_base.css",
                "css/news/all_news.css"
            ],
            "filters": "rcssmin",
            "output": "dist/all_news_css.min.css"
        },
        {
            "name": "news_css",
            "files": [
                "css/news/news_base.css",
                "css/news/news.css"
            ],
            "filters": "rcssmin",
            "output": "dist/news_css.min.css"
        },
        {
            "name": "info_css",
            "files": [
                "css/bakery/bakery_base.css",
                "css/bakery/info.css",
                "css/bakery/item_info.css"
            ],
            "filters": "rcssmin",
            "output": "dist/info_css.min.css"
        },
        {
            "name": "programs_css",
            "files": [
                "css/bakery/bakery_base.css",
                "css/bakery/programs.css"
            ],
            "filters": "rcssmin",
            "output": "dist/programs_css.min.css"
        },
        {
            "name": "search_css",
            "files": [
                "css/bakery/bakery_base.css",
                "css/bakery/search.css",
                "css/bakery/programs.css",
                "css/bakery/item_info.css",
            ],
            "filters": "rcssmin",
            "output": "dist/search_css.min.css"
        },
    ]