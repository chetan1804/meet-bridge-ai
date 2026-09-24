"""add meetings
Revision ID: 0004_add_meetings
Revises: 0003_add_organizations
"""
from alembic import op
import sqlalchemy as sa
revision="0004_add_meetings"; down_revision="0003_add_organizations"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("meetings",sa.Column("id",sa.String(36),primary_key=True),sa.Column("organization_id",sa.String(36),sa.ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False),sa.Column("created_by_id",sa.String(36),sa.ForeignKey("users.id",ondelete="RESTRICT"),nullable=False),sa.Column("title",sa.String(200),nullable=False),sa.Column("scheduled_at",sa.DateTime(timezone=True)),sa.Column("status",sa.String(20),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False)); op.create_index("ix_meetings_organization_id","meetings",["organization_id"])
def downgrade(): op.drop_index("ix_meetings_organization_id",table_name="meetings"); op.drop_table("meetings")
