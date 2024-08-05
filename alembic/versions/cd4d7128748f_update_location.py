"""update location

Revision ID: cd4d7128748f
Revises: f438b4d6003c
Create Date: 2024-08-03 08:45:54.633576

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'cd4d7128748f'
down_revision = 'f438b4d6003c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('location', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('location', sa.Column('created_at', sa.DateTime(), nullable=False))

    # Mettre à jour automatiquement les valeurs de created_at lors de l'insertion
    op.execute(text("ALTER TABLE location ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP"))

    # Mettre à jour automatiquement les valeurs de updated_at lors de la mise à jour
    op.execute(text("""
        CREATE OR REPLACE FUNCTION update_modified_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at := now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """))
    op.execute(text("CREATE TRIGGER update_location_modtime BEFORE UPDATE ON location FOR EACH ROW EXECUTE PROCEDURE update_modified_column();"))


def downgrade() -> None:
    op.drop_column('location', 'updated_at')
    op.drop_column('location', 'created_at')

    # Suppression du trigger si nécessaire
    op.execute(text("DROP TRIGGER IF EXISTS update_location_modtime ON location;"))
    op.execute(text("DROP FUNCTION IF EXISTS update_modified_column();"))
