from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.api.bootstrap import api

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.email_notification import EmailNotification
from app.models.user import User
from app.api.helpers.permissions import is_user_itself, jwt_required
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException



class EmailNotificationSchema(Schema):
    """
    API Schema for email notification Model
    """

    class Meta:
        """
        Meta class for email notification API schema
        """
        type_ = 'email-notification'
        self_view = 'v1.email_notification_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    next_event = fields.Boolean(default=False, allow_none=True)
    new_paper = fields.Boolean(default=False, allow_none=True)
    session_accept_reject = fields.Boolean(default=False, allow_none=True)
    session_schedule = fields.Boolean(default=False, allow_none=True)
    after_ticket_purchase = fields.Boolean(default=True, allow_none=True)
    event_id = fields.Integer(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.email_notification_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'email_notification_id': '<id>'},
                         schema='EventSchema',
                         type_='event'
                         )
    user = Relationship(attribute='user',
                        self_view='v1.email_notification_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'email_notification_id': '<id>'},
                        schema='UserSchema',
                        type_='user'
                        )


class EmailNotificationListPost(ResourceList):
    """
    List and create email notifications
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['user'], data)
        if not has_access('is_user_itself', id=data['user']):
            raise ForbiddenException({'source': ''}, 'You need to be the user.')

    view_kwargs = True
    methods = ['POST', ]
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}


class EmailNotificationList(ResourceList):
    """
    List all the email notification
    """

    def query(self, view_kwargs):
        """
        query method for Notifications list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(EmailNotification)
        if view_kwargs.get('id'):
            user = safe_query(self, User, 'id', view_kwargs['id'], 'id')
            query_ = query_.join(User).filter(User.id == user.id)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    decorators = (api.has_permission('is_user_itself', fetch="id", fetch_as="id"),)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification,
                  'methods': {
                      'query': query
                  }}


class EmailNotificationDetail(ResourceDetail):
    """
    Email notification detail by ID
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", fetch_as="id",
                  model=EmailNotification),)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}


class EmailNotificationRelationshipRequired(ResourceRelationship):
    """
    Email notification Relationship (Required)
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}


class EmailNotificationRelationshipOptional(ResourceRelationship):
    """
    Email notification Relationship (Optional)
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", fetch_as="id",
                                     model=EmailNotification),)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}
