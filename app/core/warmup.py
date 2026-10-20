"""Pemanasan model saat startup, tanpa pernah menjatuhkan layanan."""
import logging

from app.clients.llm_client import LLMClient, LLMError

logger = logging.getLogger(__name__)


async def warm_up_quietly(llm: LLMClient) -> None:
    """Gagal memanaskan (mis. Ollama belum menyala) hanya dicatat; request pertama tetap bisa
    berjalan, hanya lebih lambat karena model dimuat saat itu juga."""
    try:
        await llm.warm_up()
    except LLMError as exc:
        logger.warning("Pemanasan model gagal; layanan tetap berjalan: %s", exc)
    else:
        logger.info("Model siap dipakai")
