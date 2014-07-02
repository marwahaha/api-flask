# coding:utf-8

from flask import g

from database import db
from utils.models import RemovableModel, ModelForm, JsonSerializable, DbAmount

from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import case

from projects.models import Project

import datetime

"""
TODO
    * Reductions of invoices (like 15%)
    * Payments partial (accompte, et/ou en plusieurs fois (1000eur, 2000eur, 1500eur, pour un total de 4500eur))
    * Sauvegarder les factures en dur sur gogle drive / dropbox
    * Envoyer la facture en se connectant au imap/pop du propriétaire (comme ac la facture aparait dans les messages envoyes)
"""

# Invoice status :
# If due < now, overdue
# if payments = list, paid / partially paid, else not paid
class Invoice(db.Model, ModelForm, RemovableModel, JsonSerializable):
    __tablename__ = 'invoices'
    __table_args__ = (
        db.UniqueConstraint('reference', 'project_id', name='_project_reference'),
    )

    __jsonserialize__ = ['id', 'reference', 'created', 'due', 'removed', 'project', 'message', 'discount', 'discount_percent',
                         ('get_client', 'client'), 'project', ('get_amount', 'amount'), ('get_amount_vat', 'amount_vat'),
                         ('get_total_paid', 'paid'), 'currency', ('get_status', 'status'),
                         ('get_payments', 'payments'), ('get_entries', 'entries')]

    id = db.Column(db.Integer, primary_key=True)

    reference = db.Column(db.String(50), nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    due = db.Column(db.DateTime, nullable=True)
    removed = db.Column(db.DateTime, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    project = relationship('Project')

    client_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    client = relationship('Member', backref=backref('invoices'))

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    project = relationship('Project', backref=backref('invoices'))

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('invoices'))

    currency = db.Column(db.String(3), nullable=False, default="USD")
    discount = db.Column(DbAmount, nullable=True)
    discount_percent = db.Column('is_discount_percent', db.Boolean, nullable=False, default=True)

    message = db.Column(db.Text, nullable=True)
    tax = db.Column(DbAmount, nullable=True)

    entries = relationship('InvoiceEntry', order_by="InvoiceEntry.sort")
    payments = relationship('InvoicePayment')

    def __repr__(self):
        return self.reference

    def get_amount(self):
        amount = 0
        for entry in self.entries:
            if not entry.optional:
                amount += entry.quantity * entry.amount

        return amount

    def get_amount_vat(self):
        amount = self.get_amount()
        if self.tax is None or self.tax == 0:
            return amount

        return float("{:.2f}".format(amount * (1 + (self.tax/100))))

    def get_total(self):
        amount = self.get_amount_vat()

        if self.discount:
            if self.discount_percent:
                amount = amount - ((amount * self.discount) / 100)
            else:
                amount -= self.discount

        return amount

    def get_total_paid(self):
        amount = 0
        for payment in self.payments:
            amount += payment.amount

        return amount

    def get_entries(self):
        returned_entries = []
        for entry in self.entries:
            returned_entries.append(entry.to_json())

        return returned_entries

    def get_payments(self):
        returned_payments = []
        for payment in self.payments:
            returned_payments.append(payment.to_json())

        return returned_payments

    def get_client(self):
        if not self.client:
            return None

        return {
            'id': self.client.id,
            'display': self.client.display,
            'email': self.client.get_email(),
            'address': self.client.address,
            'business_number': self.client.business_number
        }

    def get_status(self):
        """
        DRAFT = No project
        APPROVED = In project
        PAID / PARTIALLY / OVERPAID = Payment.length > 0
        LATE = due < now
        """

        if len(self.payments) > 0:
            amount = self.get_amount_vat()
            paid = self.get_total_paid()

            if amount == paid:
                return "PAID"
            else:
                if amount < paid:
                    return "OVERPAID"
                elif self.due < datetime.datetime.utcnow():
                    return "LATE"
                else:
                    return "PARTIALLY PAID"
                    

        if not self.project_id:
            return "DRAFT"

        if self.due < datetime.datetime.utcnow():
            return "LATE"

        return "APPROVED"


    @classmethod
    def find_by_id(cls, id):
        """
        Return the invoice of given id,
        Verify agains't registered projects if not admin
        """
        query = cls.query.filter(cls.id == id).filter(cls.organization_id == g.organization.id)

        if g.member.admin:
            return query.first()

        invoice_ids = []
        for invoice in g.member.invoices:
            invoice_ids.append(invoice.id)

        return query.filter(cls.id.in_(invoice_ids)).first()

    @classmethod
    def find(cls, form):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.organization_id == g.organization.id)

        if not g.member.admin:
            # Assuring that the asking user as the rights to see this user
            invoice_ids = []
            for invoice in g.member.invoices:
                invoice_ids.append(invoice.id)

            query = query.filter(cls.id.in_(invoice_ids))

        return cls.paginate(query, form)

    @classmethod
    def filter_by_project_id(cls, query, field):
        query = query.filter(cls.project_id == field.data)

        return query

    @classmethod
    def filter_by_client_id(cls, query, field):
        query = query.filter(cls.client_id == field.data)

        return query

    @classmethod
    def filter_by_amount(cls, query, field):
        query = query.join(cls.entries).group_by(cls.id).having(func.sum(case([(InvoiceEntry.optional == True, InvoiceEntry.amount * InvoiceEntry.quantity)], else_=0)) == int(field.data * 100))

        return query

    @classmethod
    def filter_by_status(cls, query, field):
        if field.data == "DRAFT":
            query = query.filter(cls.project_id == None)
        elif field.data == "APPROVED":
            query = query.filter(cls.project_id != None)
        elif field.data == "LATE":
            query = query.filter(cls.due < datetime.datetime.utcnow())
        elif field.data == "PAID":
            query = query.join(cls.entries).join(cls.payments).group_by(cls.id).having(func.sum(case([(InvoiceEntry.optional == True, InvoiceEntry.amount * InvoiceEntry.quantity)], else_=0)) == func.sum(InvoicePayment.amount))
        elif field.data == "PARTIALLY":
            query = query.join(cls.entries).join(cls.payments).group_by(cls.id).having(func.sum(case([(InvoiceEntry.optional == True, InvoiceEntry.amount * InvoiceEntry.quantity)], else_=0)) > func.sum(InvoicePayment.amount)).having(func.sum(InvoicePayment.amount) > 0)
        elif field.data == "OVERPAID":
            query = query.join(cls.entries).join(cls.payments).group_by(cls.id).having(func.sum(case([(InvoiceEntry.optional == True, InvoiceEntry.amount * InvoiceEntry.quantity)], else_=0)) < func.sum(InvoicePayment.amount))

        return query

    @classmethod
    def order_by_project(cls, query, order="asc"):
        return query.join(cls.project, aliased=True).order_by(getattr(cls.project.display, order.lower())())

    @classmethod
    def order_by_client(cls, query, order="asc"):
        return query.join(cls.client, aliased=True).order_by(getattr(cls.client.display, order.lower())())


class InvoiceEntry(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'invoice_entries'

    __jsonserialize__ = ['id', 'description', 'amount', 'quantity', 'optional', 'sort', ('get_currency', 'currency'), ('get_total', 'total')]

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

    amount = db.Column(DbAmount, nullable=False)
    quantity = db.Column(db.SmallInteger, nullable=False, default=1)

    sort = db.Column(db.SmallInteger, nullable=False, default=1)

    optional = db.Column('is_optional', db.Boolean, nullable=False, default=False) # An option, like airbags (old school) (not included in the total)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    invoice = relationship('Invoice')

    def __repr__(self):
        return self.description

    def get_currency(self):
        return self.invoice.currency

    def get_total(self):
        return float("{:.2f}".format(self.amount * self.quantity))

    @classmethod
    def find_by_id(cls, invoice_id, id):
        """
        Return the invoice of given id,
        Verify agains't registered projects if not admin
        """
        query = cls.query.filter(cls.id == id) \
                .filter(cls.invoice_id == invoice_id) \
                .join(Invoice) \
                .filter(Invoice.organization_id == g.organization.id)

        if g.member.admin:
            return query.first()

        invoice_ids = []
        for invoice in g.member.invoices:
            invoice_ids.append(invoice.id)

        return query.filter(Invoice.id.in_(invoice_ids)).first()

    @classmethod
    def find(cls, form, invoice_id):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.invoice_id == invoice_id) \
                .join(Invoice) \
                .filter(Invoice.organization_id == g.organization.id)

        if not g.member.admin:
            # Assuring that the asking user as the rights to see this user
            invoice_ids = []
            for invoice in g.member.invoices:
                invoice_ids.append(invoice.id)

            query = query.filter(Invoice.id.in_(invoice_ids))

        return cls.paginate(query, form)



class InvoiceItem(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'invoice_items'

    __jsonserialize__ = ['id', 'description', 'amount', 'sort', 'optional', ('get_currency', 'currency')]

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

    amount = db.Column(DbAmount, nullable=False)

    sort = db.Column(db.SmallInteger, nullable=False, default=1)

    optional = db.Column('is_optional', db.Boolean, nullable=False, default=False) # An option, like airbags (old school) (not included in the total)

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    organization = relationship('Organization', backref=backref('invoice_items'))

    def __repr__(self):
        return self.description

    def get_currency(self):
        return self.organization.currency

    @classmethod
    def find_by_id(cls, id):
        """
        Return the invoice of given id,
        Verify agains't registered projects if not admin
        """
        query = cls.query.filter(cls.id == id).filter(cls.organization_id == g.organization.id)

        return query.first()

    @classmethod
    def find(cls, form):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.organization_id == g.organization.id)

        return cls.paginate(query, form)


class InvoicePayment(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'invoice_payments'
    __jsonserialize__ = ['id', 'amount', 'paid', 'created', ('get_currency', 'currency')]

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(DbAmount, nullable=False)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    invoice = relationship('Invoice')

    paid = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return self.amount

    def get_currency(self):
        return self.invoice.currency

    @classmethod
    def find_by_id(cls, invoice_id, id):
        """
        Return the invoice of given id,
        Verify agains't registered projects if not admin
        """
        query = cls.query.filter(cls.id == id) \
                .filter(cls.invoice_id == invoice_id) \
                .join(Invoice) \
                .filter(Invoice.organization_id == g.organization.id)

        if g.member.admin:
            return query.first()

        invoice_ids = []
        for invoice in g.member.invoices:
            invoice_ids.append(invoice.id)

        return query.filter(Invoice.id.in_(invoice_ids)).first()

    @classmethod
    def find(cls, form, invoice_id):
        """
        Returns a paginate instance of a list
        """
        query = cls.query_from_base_filter(form)
        query = query.filter(cls.invoice_id == invoice_id) \
                .join(Invoice) \
                .filter(Invoice.organization_id == g.organization.id)

        if not g.member.admin:
            # Assuring that the asking user as the rights to see this user
            invoice_ids = []
            for invoice in g.member.invoices:
                invoice_ids.append(invoice.id)

            query = query.filter(Invoice.id.in_(invoice_ids))

        return cls.paginate(query, form)

InvoiceHistoryTypes = ('GENERATED', 'SENT', 'PAID')

class InvoiceHistory(db.Model, ModelForm, JsonSerializable):
    __tablename__ = 'invoice_histories'
    __jsonserialize__ = ['id', 'created', 'description', 'pdf', 'member', 'type', 'misc', 'invoice_id']

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    pdf = db.Column(db.String(250), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    member = relationship('Invoice')
    status = db.Column(db.Enum(*InvoiceHistoryTypes))
    misc = db.Column(db.Text, nullable=True)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    invoice = relationship('Invoice')


    def __repr__(self):
        return self.description