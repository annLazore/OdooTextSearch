{
    'name': "Full-text search",
    'version': '1.0',
    'depends': ['base'],
    'author': "Anna",
    'category': 'Search',
    'description': """
    Full-text search 
    """,
    # todo write description

    'data': [
        'security/ir.model.access.csv',
        'views/full_text_search_main.xml',
        'views/search_menu.xml',
    ],

    'application': True,
}