"""
Marshmallow schemas for API input validation.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class EventCreateSchema(Schema):
    """Schema for creating a new event."""
    road_id = fields.Integer(required=True, validate=validate.Range(min=1))
    type = fields.String(
        required=True,
        validate=validate.OneOf(['Accident', 'Construction', 'Congestion', 'Control'])
    )
    description = fields.String(allow_none=True, validate=validate.Length(max=500))
    position = fields.String(allow_none=True, validate=validate.Length(max=100))
    timestamp = fields.DateTime(allow_none=True)
    status = fields.String(
        load_default='active',
        validate=validate.OneOf(['active', 'resolved', 'cancelled'])
    )
    severity = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=5)
    )
    user_id = fields.Integer(allow_none=True, validate=validate.Range(min=1))


class TrafficQuerySchema(Schema):
    """Schema for traffic history query parameters."""
    start = fields.DateTime(allow_none=True)
    end = fields.DateTime(allow_none=True)

    @validates('start')
    def validate_start(self, value):
        """Ensure start time is not in the future."""
        from datetime import datetime, timezone
        if value and value > datetime.now(timezone.utc):
            raise ValidationError("Start time cannot be in the future.")


class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    limit = fields.Integer(
        load_default=10,
        validate=validate.Range(min=1, max=100)
    )
    page = fields.Integer(
        load_default=1,
        validate=validate.Range(min=1)
    )
    offset = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=0)
    )


class EventFilterSchema(PaginationSchema):
    """Schema for event filtering."""
    status = fields.String(
        load_default='active',
        validate=validate.OneOf(['active', 'resolved', 'cancelled', 'all'])
    )
    severity = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=5)
    )


class ExportFormatSchema(Schema):
    """Schema for data export requests."""
    format = fields.String(
        load_default='csv',
        validate=validate.OneOf(['csv', 'excel', 'json'])
    )
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
