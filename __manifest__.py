{
    "name": "Asset Form",
    "version": "17.0.1.0.0",
    "summary": "Asset Request Form Management",
    "description": """
        Simple module for printing asset forms.
    """,
    "author": "Joseph Aniken Naval",
    "category": "Operation",
    "license": "LGPL-3",
    "depends": [
        "base", "hr", 'mail',
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/asset_form_views.xml",
        "views/asset_model_views.xml",
        "views/asset_menus.xml",
        "report/asset_form_report.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
} # type: ignore