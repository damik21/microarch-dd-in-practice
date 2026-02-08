"""Create orders, couriers and storage_places tables.

Revision ID: 001
Revises:
Create Date: 2025-02-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем enum для статусов заказа
    order_status_enum = postgresql.ENUM(
        "CREATED",
        "ASSIGNED",
        "COMPLETED",
        name="order_status",
        create_type=True,
    )
    order_status_enum.create(op.get_bind())

    # Создаем таблицу couriers
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

    # Создаем таблицу storage_places
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

    # Создаем индекс для courier_id в storage_places
    op.create_index(
        "ix_storage_places_courier_id",
        "storage_places",
        ["courier_id"],
    )

    # Создаем таблицу orders
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

    # Создаем индекс для courier_id в orders
    op.create_index(
        "ix_orders_courier_id",
        "orders",
        ["courier_id"],
    )


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_index("ix_orders_courier_id", "orders")
    op.drop_table("orders")

    op.drop_index("ix_storage_places_courier_id", "storage_places")
    op.drop_table("storage_places")
    op.drop_table("couriers")

    # Удаляем enum
    postgresql.ENUM(name="order_status").drop(op.get_bind())
