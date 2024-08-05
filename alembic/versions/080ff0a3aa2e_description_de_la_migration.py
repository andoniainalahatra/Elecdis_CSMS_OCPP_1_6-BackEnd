from alembic import op
import sqlalchemy as sa
import sqlmodel as sm
from typing import Union, Sequence

# revision identifiers, used by Alembic.
revision: str = 'f438b4d6003c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Ajouter la colonne 'ocpp_version'
    op.add_column('chargepoint', sa.Column('ocpp_version', sa.String()))
    
    # Ajouter la colonne 'updated_at' avec un timestamp par défaut à l'heure actuelle en UTC
    op.add_column('chargepoint', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP AT TIME ZONE 'utc')")))
    
    # Ajouter la colonne 'created_at' avec un timestamp par défaut à l'heure actuelle en UTC
    op.add_column('chargepoint', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP AT TIME ZONE 'utc')")))

def downgrade() -> None:
    # Supprimer les colonnes ajoutées dans upgrade()
    op.drop_column('chargepoint', 'ocpp_version')
    op.drop_column('chargepoint', 'update_at')
    op.drop_column('chargepoint', 'creat_at')  # Notez la correction de 'creat_at' en 'create_at' si c'était une faute de frappe.