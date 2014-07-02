# coding:utf-8

from weasyprint import HTML, CSS
from flask import current_app, g, render_template

from invoices.models import InvoiceHistory

import hashlib
import json

import boto
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key
from boto.s3.bucket import Bucket

class AmazonS3(object):
    def __init__(self):
        self.conn = S3Connection(current_app.config['AWS_ACCESS_KEY'], current_app.config['AWS_SECRET_KEY'])

    def _get_bucket(self, name):
        name = '2leadin-{1}'.format(current_app.config['AWS_ACCESS_KEY'].lower(), name)

        if not self.conn.lookup(name):
            return self.conn.create_bucket(name, location=Location.EU)
        else:
            return self.conn.get_bucket(name)

    def get_invoice_key(self, name, metadata=None):
        name = '{0}/organizations/{1}/invoices/{2}'.format(str(g.application.id), str(g.organization.id), name)
        key = Key(bucket=self._get_bucket('invoices'), name=name)
        for key_name in metadata:
            key.set_metadata(key_name, metadata[key_name])

        return key


    def get_logo_key(self, name, metadata=None):
        name = '{0}/organizations/{1}/{2}'.format(str(g.application.id), str(g.organization.id), name)
        return Key(bucket=self._get_bucket('logos'), name=name, **kwargs)

    def get_file_key(self, project, file_path, metadata=None):
        name = '{0}/organizations/{1}/projects/{2}/files/{3}'.format(str(g.application.id), str(g.organization.id), project, file_path)
        return Key(bucket=self._get_bucket('files'), name=name, **kwargs)

    def get_applications_logo_key(self, name, metadata=None):
        name = '{0}/{1}'.format(str(g.application.id), name)
        return Key(bucket=self._get_bucket('applications'), name=name, **kwargs)


def get_invoice(invoice):
    if not invoice:
        return None

    # Faster than rendering the template and md5ize it
    organization_dict = {
        'display': g.organization.display, 
        'address': g.organization.address,
        'business_number': g.organization.business_number,
        'show_payments': g.organization.show_payments
    }

    hash_str = json.dumps(invoice.to_json()) + json.dumps(organization_dict)

    s3 = AmazonS3()
    invoice_key = s3.get_invoice_key('{0}-{1}.pdf'.format(str(invoice.id), hashlib.md5(hash_str).hexdigest()), {'content-type': 'application/pdf'})

    if not invoice_key.exists():
        invoice_key.set_contents_from_string(_render_invoice(invoice), encrypt_key=True)
        invoice_key.set_acl('private')

        history = InvoiceHistory()
        history.description = 'Generated PDF'
        history.pdf = invoice_key.key
        history.status = 'GENERATED'
        history.member_id = g.member.id
        history.invoice_id = invoice.id
        history.save()

    return invoice_key

def _render_invoice(invoice):
    invoice.amount = invoice.get_amount() or 0
    invoice.total_payments = 0
    invoice.balance = 0

    for payment in invoice.payments:
        invoice.total_payments += payment.amount

    invoice.balance = invoice.amount * (1 + (invoice.tax/100))

    if invoice.discount:
        if invoice.discount_percent:
            invoice.balance -= (invoice.balance * invoice.discount) / 100
        else:
            invoice.balance -= invoice.discount

    invoice.balance -= invoice.total_payments

    result = render_template('v1/pdf/invoice.html', invoice=invoice, organization=g.organization)

    return HTML(string=result) \
            .render(stylesheets=[CSS('{0}/templates/css/invoice.css'.format(current_app.config.get('APPLICATION_PATH')))]).write_pdf(None)