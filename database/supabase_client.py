"""Cliente Singleton de Supabase."""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_client: Client | None = None


def get_supabase() -> Client:
    """Retorna la instancia única del cliente Supabase."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Configura SUPABASE_URL y SUPABASE_KEY en .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
