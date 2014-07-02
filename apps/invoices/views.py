# coding:utf-8

from flask import Blueprint, g, abort, send_file, request, current_app

from flask.ext.mail import Mail, Message, sanitize_address


from utils.api import BaseAPI, FormApiError
from utils.decorators import url_access, authenticated
from utils import amazons3

from .forms import *
from .models import *

from members.models import Member
from projects.models import Project
from invoices.models import InvoiceHistory

import datetime
import StringIO


class InvoiceAPI(BaseAPI):
    def __init__(self):
        self.form_listing = InvoiceListing
        self.form = InvoiceForm
        self.model = Invoice

    def check_write_access(self, type, **kwargs):
        return g.member.admin

    def post_create(self, form, instance):
        if not instance.currency:
            instance.currency = g.organization.currency

        instance.organization_id = g.organization.id
        instance.created = datetime.datetime.utcnow()

    def post_update(self, form, instance, id):
        if not instance.currency:
            instance.currency = g.organization.currency


invoices = Blueprint('invoices', __name__)
InvoiceAPI.register(invoices, '/')

@invoices.route('/<int:invoice_id>/pdf')
@url_access
def export_as_pdf(invoice_id):
    """
    TODO :
        When generatig file, saving as invoice.id-md5(invoice.to_dict().to_string()).pdf
            Deleting old invoice.id-* before
            ~ This will ensure that only one instance of the invoice is always present
            ~ And that if changes are made, the pdf will be automatically regenerated


        Create the correct css
    """
    invoice = Invoice.find_by_id(invoice_id)
    if not invoice:
        return abort(404)

    invoice_key = amazons3.get_invoice(invoice)
    strIO = StringIO.StringIO()
    strIO.write(invoice_key.get_contents_as_string())
    strIO.seek(0)

    return send_file(strIO, mimetype='application/pdf')

@invoices.route('/<int:invoice_id>/send', methods=['POST'])
@authenticated
def send_pdf_by_email(invoice_id):
    form = InvoiceEmail(request.form)

    if not form.validate():
        return form.errors_as_json()

    invoice = Invoice.find_by_id(invoice_id)
    if not invoice:
        return abort(404)

    message = Message(form.subject.data.encode('utf-8'), sender=(g.member.display, g.member.get_email().encode('utf-8')))
    message.add_recipient(sanitize_address((form.name.data, form.email.data)))
    message.body = form.message.data.encode('utf-8')

    invoice_key = amazons3.get_invoice(invoice)
    message.attach("Invoice_{0}.pdf".format(invoice.reference), "application/pdf", invoice_key.get_contents_as_string())

    mail = Mail()
    mail.init_app(current_app)
    mail.send(message)

    history = InvoiceHistory()
    history.description = 'Sent email to {0}'.format(message.recipients[0])
    history.pdf = invoice_key.key
    history.status = 'SENT'
    history.misc = "{0}\n\n{1}".format(message.subject, message.body)
    history.member_id = g.member.id
    history.invoice_id = invoice.id
    history.save()

    return 'sent', 200

class InvoiceEntryAPI(BaseAPI):
    def __init__(self):
        self.form_listing = InvoiceEntryListing
        self.form = InvoiceEntryForm
        self.model = InvoiceEntry

    def check_write_access(self, type, **kwargs):
        return g.member.admin

    def post_create(self, form, instance, invoice_id):
        instance.invoice_id = invoice_id


invoice_entries = Blueprint('invoice_entries', __name__)
InvoiceEntryAPI.register(invoice_entries, '/<int:invoice_id>/entries/')


class InvoiceItemAPI(BaseAPI):
    def __init__(self):
        self.form_listing = InvoiceItemListing
        self.form = InvoiceItemForm
        self.model = InvoiceItem

    def check_write_access(self, type, **kwargs):
        return g.member.admin

    def post_create(self, form, instance):
        instance.organization_id = g.organization.id


invoice_items = Blueprint('invoice_items', __name__)
InvoiceItemAPI.register(invoice_items, '/items/')


class InvoicePaymentAPI(BaseAPI):
    def __init__(self):
        self.form_listing = InvoicePaymentListing
        self.form = InvoicePaymentForm
        self.model = InvoicePayment

    def check_write_access(self, type, **kwargs):
        return g.member.admin

    def post_create(self, form, instance, invoice_id):
        invoice = Invoice.find_by_id(invoice_id)
        if not invoice:
            return abort(404)

        instance.invoice_id = invoice_id
        instance.created = datetime.datetime.utcnow()

        history = InvoiceHistory()
        history.created = instance.created
        history.description = 'Payment of {0} {1}'.format(instance.amount, invoice.currency)
        history.status = 'PAID'
        history.member_id = g.member.id
        history.invoice_id = invoice_id
        history.save()

    def post_update(self, form, instance, invoice_id):
        invoice = Invoice.find_by_id(invoice_id)
        if not invoice:
            return abort(404)

        InvoiceHistory.query \
            .filter(InvoiceHistory.status == 'PAID') \
            .filter(InvoiceHistory.invoice_id == invoice_id) \
            .filter(InvoiceHistory.created == instance.created) \
            .delete()

        history = InvoiceHistory()
        history.created = instance.created
        history.description = 'Payment of {0} {1}'.format(instance.amount, invoice.currency)
        history.status = 'PAID'
        history.member_id = g.member.id
        history.invoice_id = invoice_id
        history.save()

    def post_delete(self, instance, invoice_id):
        invoice = Invoice.find_by_id(invoice_id)
        if not invoice:
            return abort(404)

        InvoiceHistory.query \
            .filter(InvoiceHistory.status == 'PAID') \
            .filter(InvoiceHistory.invoice_id == invoice_id) \
            .filter(InvoiceHistory.created == instance.created) \
            .delete()


invoice_payments = Blueprint('invoice_payments', __name__)
InvoicePaymentAPI.register(invoice_payments, '/<int:invoice_id>/payments/')

app = (invoices, invoice_entries, invoice_items, invoice_payments)
