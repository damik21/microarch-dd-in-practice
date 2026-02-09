from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    order_status_enum = postgresql.ENUM(
        "CREATED",
        "ASSIGNED",
        "COMPLETED",
        name="order_status",
        create_type=True,
    )
    order_status_enum.create(op.get_bind())

    op.create_table(
        "couriers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("speed", sa.Integer(), nullable=False),
        sa.Column("location_x", sa.Integer(), nullable=False),
        sa.Column("location_y", sa.Integer(), nullable=False),
    )

    op.create_table(
        "storage_places",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "courier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("couriers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("total_volume", sa.Integer(), nullable=False),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            default=None,
        ),
    )

    op.create_table(
        "orders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "courier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("couriers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("location_x", sa.Integer(), nullable=False),
        sa.Column("location_y", sa.Integer(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            order_status_enum,
            nullable=False,
            default="CREATED",
        ),
    )


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("storage_places")
    op.drop_table("couriers")

    postgresql.ENUM(name="order_status").drop(op.get_bind())
