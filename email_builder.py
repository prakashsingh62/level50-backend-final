# email_builder.py

def build_email_html(blocks):
    if not blocks:
        return "<p>No RFQs need attention today.</p>"

    html = '''
    <html>
    <head>
    <style>
    body { font-family: Arial, sans-serif; font-size: 14px; }
    table { border-collapse: collapse; width: 100%; }
    td { border: 1px solid #ccc; padding: 6px; word-wrap: break-word; }
    @media only screen and (max-width: 480px) {
        table, td {
            font-size: 13px !important;
            width: 100% !important;
        }
    }
    </style>
    </head>
    <body>
    <h2>Daily RFQ Reminder (Level-50 Smart Assistant)</h2>
    '''

    for b in blocks:
        html += b

    html += "</body></html>"
    return html
