from pydantic import BaseModel, ConfigDict


class CommandsName(BaseModel):
    COMMAND_UPDATE_TEXT: str = "/update_kb_text"
    COMMAND_UPDATE_VOICE: str = "/update_kb_voice"
    COMMAND_EXIT: list[str] = ["/exit", "/quit", "q"]
    COMMAND_SAVE_SESSION: str = "/save_session"
    COMMAND_LOAD_SESSION: str = "/load_session"
    COMMAND_CHANGE_PROMPT: str = "/change_prompt"

    model_config = ConfigDict()
